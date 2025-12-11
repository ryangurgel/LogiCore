#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Motor simbólico brutal, agora com o modelo "Predicado + Roles Nomeados" (SPO evoluído).

- Conhecimento vem de banco.json (lista de fatos e regras).
- Forma preferida de fato:
    fact = {
        "predicate": str,
        "roles": { role_name: value },
        "weight": number,
        "context": [tags]
    }
  SPO vira caso especial: predicate=P, roles={"s": S, "o": O}. T/L/C/tempo viram apenas roles nomeados.
- Compatibilidade: ainda aceitamos "S"/"P"/"O" nos dados e derivamos roles automaticamente.
- Motorzão único: BrutalEngine.explain(goal)
    * goal = {"S": ..., "P": ..., "O": ..., "T": ..., "L": ..., "C": ...}
      (None = coringa / wildcard, strings começando com "?" = variáveis)

Suporta:
- Dedução com "é" (transitividade, herança via cadeia de "é").
- Causalidade + planejamento simples: "faz" + "pode_fazer" + "causa".
- Abdução: "explica" com lista de sintomas -> doenças que têm "sintoma_de"/"sintoma_tipico_de".
- Leis: "melhor_para_argumentar" com:
    aplica_a + vigência + revogação + precedentes + conflitos + exceções.
- Default fraco via "nao_provavel" (negação como falha simplificada).
- Tratamento de tempo (T) em fatos e goals com intervalos ([start, end]).
- Match numérico simples: goal["O"] como string ">120", "<=3.5", etc.
- Variáveis lógicas com unificação simples, bindings por estado.
- Memoização de estados (unsat + bindings) + beam limitado por passo.
- Penalidade de complexidade por fato usado na explicação.
- Analogia simbólica via "similar_a" + vizinhança, com peso fraco.
- Detecção de contradições (ex.: "é" vs "nao_é", "aplica_a" vs "nao_aplica_a").
- Regras declarativas: head/body como mais um operador normal.

Este arquivo é autocontido. Você só precisa de um banco.json ao lado dele.
"""

import json
import math
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------
# KnowledgeBase: carrega banco.json em fatos + regras
# ---------------------------------------------------------


class KnowledgeBase:
    """
    Grafo simbólico baseado em fatos S, P, O, opcionalmente T, L, C e peso w.
    Carrega de banco.json e mantém índices por S, P, O.
    Também guarda regras declarativas.
    """

    def __init__(self):
        self.facts: List[Dict[str, Any]] = []
        self.by_s: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
        self.by_p: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
        self.by_o: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)

        # regras declarativas
        self.rules: List[Dict[str, Any]] = []

    @staticmethod
    def _normalize_fact_shape(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normaliza um fato (novo modelo ou S/P/O legados) para o formato interno."""

        if raw is None:
            return None

        # novo modelo: predicate + roles nomeados
        if raw.get("predicate") is not None:
            predicate = raw.get("predicate")
            roles = dict(raw.get("roles") or {})
            context = list(raw.get("context") or [])
            weight = float(raw.get("weight", raw.get("w", 1.0)))
        else:
            # modo legado SPO(TLC)
            predicate = raw.get("P")
            roles = {}
            if "S" in raw:
                roles["s"] = raw.get("S")
            if "O" in raw:
                roles["o"] = raw.get("O")
            if "T" in raw:
                roles["t"] = raw.get("T")
            if "L" in raw:
                roles["l"] = raw.get("L")
            if "C" in raw:
                roles["c"] = raw.get("C")
            context = list(raw.get("context") or [])
            weight = float(raw.get("w", 1.0))

        normalized = {
            "predicate": predicate,
            "roles": roles,
            "context": context,
            "w": weight,
            "source": raw.get("source", "kb"),
        }

        # campos derivativos para compatibilidade com o motor legado
        normalized["S"] = roles.get("s")
        normalized["P"] = predicate
        normalized["O"] = roles.get("o")
        normalized["T"] = roles.get("t")
        normalized["L"] = roles.get("l")
        normalized["C"] = roles.get("c")

        return normalized

    def add_fact(self, fact: Dict[str, Any]):
        fact = dict(fact)
        self.facts.append(fact)

        # índices simples
        S = fact.get("S")
        P = fact.get("P")
        O = fact.get("O")

        self.by_s[S].append(fact)
        self.by_p[P].append(fact)

        # índice por O transforma O em chave hashable
        O_key = repr(O)
        self.by_o[O_key].append(fact)

    def load_json(self, path: str):
        """
        Carrega fatos e regras de um arquivo JSON.

        Formato esperado de banco.json:
        [
          {"S": "...", "P": "...", "O": "...", "T": ..., "L": ..., "C": ..., "w": 1.0},
          {
            "rule": true,
            "name": "regra_x",
            "head": {S,P,O,T,L,C},
            "body": [ {S,P,O,...}, ... ],
            "w": 1.5
          },
          ...
        ]
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo de conhecimento não encontrado: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("banco.json deve ser uma lista de fatos/regras (objetos JSON).")

        for raw in data:
            # entrada de REGRA
            if raw.get("rule") is True:
                head_raw = raw.get("head")
                body_raw = raw.get("body")
                if not isinstance(head_raw, dict) or not isinstance(body_raw, list):
                    continue

                head = self._normalize_fact_shape(head_raw)
                body: List[Dict[str, Any]] = []
                for clause in body_raw:
                    norm_clause = self._normalize_fact_shape(clause)
                    if norm_clause and norm_clause.get("predicate") is not None:
                        body.append(norm_clause)

                if not head or head.get("predicate") is None or not body:
                    continue

                nome = raw.get("name") or f"regra_{len(self.rules)+1}"
                w = float(raw.get("w", 1.0))
                self.rules.append(
                    {
                        "name": nome,
                        "head": head,
                        "body": body,
                        "w": w,
                    }
                )
                continue

            # FATO normal (novo modelo ou SPO legado)
            fact = self._normalize_fact_shape(raw)
            if not fact or fact.get("predicate") is None:
                continue
            self.add_fact(fact)


# ---------------------------------------------------------
# BrutalEngine: motorzão único de explicação
# ---------------------------------------------------------


class BrutalEngine:
    """
    Motorzão de explicação:
    Dado um goal (S, P, O, T, L, C opcionais), tenta achar explicações no grafo.

    Tudo é uma busca de explicações, com operadores simbólicos:
    - match direto de fatos
    - "é"        -> transitividade, herança
    - "faz"      -> expansão com "pode_fazer" + "causa"
    - "causa"    -> encadeamento causal
    - "explica"  -> abdução via sintomas
    - "melhor_para_argumentar" -> heurística de leis
    - regras declarativas (head/body)
    - "nao_provavel" -> default fraco (negação como falha simples)
    - analogia simbólica

    Extras:
    - variáveis (strings começando com "?") + unificação
    - estado com bindings: {"?x": "gorila", "?lei": "lei_123", ...}
    - memo de estados e beam limitado por passo
    - penalidade de complexidade por fato
    - detecção de contradições básicas
    """

    def __init__(self, kb: KnowledgeBase, complexity_penalty: float = 0.1):
        self.kb = kb
        self.complexity_penalty = complexity_penalty

        # pares de predicados que se contradizem (simbólico, sem NLP)
        self.contradictory_pairs = {
            frozenset(("é", "nao_é")),
            frozenset(("aplica_a", "nao_aplica_a")),
        }

        # contador pra ids de fatos em explicação
        self._next_fact_id = 0

        # força relativa dos operadores (peso multiplicador no score incremental)
        self.operator_strengths: Dict[str, float] = {
            "direct": 3.0,
            "trans_é": 2.0,
            "planejamento": 2.0,
            "causal": 2.0,
            "abducao": 1.0,
            "analogico": 0.7,
            "lei": 2.0,
            "regra": 2.0,
            "naf": 0.1,
        }

        # limite de expansões por operador (controle de “atenção simbólica”)
        self.max_expansions_per_operator: Dict[str, int] = {
            "_op_match_direct": 50,
            "_expand_trans_isa": 20,
            "_expand_faz_causa": 20,
            "_expand_causal_chain": 20,
            "_expand_abducao_explica": 15,
            "_expand_melhor_lei": 10,
            "_op_regras": 25,
            "_op_naf": 10,
            "_expand_analogia": 10,
        }

        # lista explícita de operadores (ordem é leve, mas quem manda é o score)
        self.operators = [
            self._op_match_direct,
            self._expand_trans_isa,
            self._expand_faz_causa,
            self._expand_causal_chain,
            self._expand_abducao_explica,
            self._expand_melhor_lei,
            self._op_regras,
            self._op_naf,
            self._expand_analogia,
        ]

    # -------------------------- Helpers internos --------------------------

    def _new_fact_id(self) -> str:
        self._next_fact_id += 1
        return f"h#{self._next_fact_id}"

    def _wrap_fact(
        self,
        base: Dict[str, Any],
        derived_by: str,
        from_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Copia um fato base (kb ou sintético) e adiciona metadados de explicação:
          - id         -> identificador único
          - derived_by -> "direct", "regra", "analogico", "abducao", "lei", "naf", ...
          - from       -> lista de ids de suporte (por enquanto simples)
          - source     -> "kb" ou "derived"
        """
        f = dict(base)
        f["id"] = self._new_fact_id()
        f["derived_by"] = derived_by
        f["from"] = list(from_ids or [])
        f.setdefault("w", 1.0)
        # se vier do KB, mantemos "kb", senão default "derived"
        if "source" not in f:
            f["source"] = "derived"
        return f

    @staticmethod
    def _log_score(weight: float) -> float:
        """Score incremental baseado no peso do fato: log1p evita explosão."""
        return math.log1p(max(weight, 0.0))

    def _score_increment_for_fact(self, fact: Dict[str, Any]) -> float:
        """
        Score incremental padrão:
          log1p(w) * operator_strength[derived_by]
        """
        w = float(fact.get("w", 1.0))
        base = self._log_score(w)
        derived_by = fact.get("derived_by")
        strength = self.operator_strengths.get(derived_by, 1.0)
        return base * strength

    @staticmethod
    def _is_var(value: Any) -> bool:
        """Variáveis são strings que começam com '?'."""
        return isinstance(value, str) and value.startswith("?")

    @staticmethod
    def _apply_bindings_to_goal(
        goal: Dict[str, Any], bindings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Substitui variáveis do goal pelos valores em bindings, se existirem."""
        new_goal = {}
        for k in ("S", "P", "O", "T", "L", "C"):
            v = goal.get(k)
            if isinstance(v, str) and v.startswith("?") and v in bindings:
                new_goal[k] = bindings[v]
            else:
                new_goal[k] = v
        return new_goal

    @staticmethod
    def _unify_var(
        var: str, value: Any, bindings: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Unifica uma variável 'var' com 'value' dentro de bindings.
        """
        assert var.startswith("?")
        if var in bindings:
            if bindings[var] == value:
                return bindings
            return None
        new_bindings = dict(bindings)
        new_bindings[var] = value
        return new_bindings

    @staticmethod
    def _parse_numeric_condition(value: Any) -> Optional[Tuple[str, float]]:
        """
        Interpreta goal["O"] como condição numérica simples.
        Exemplos aceitos:
          ">120"  -> ( ">", 120.0 )
          ">=50"  -> ( ">=", 50.0 )
          "<=10"  -> ( "<=", 10.0 )
          "<3.14" -> ( "<", 3.14 )
        """
        if not isinstance(value, str):
            return None
        val = value.strip()
        for op in (">=", "<=", ">", "<"):
            if val.startswith(op):
                try:
                    num = float(val[len(op):].strip())
                    return op, num
                except ValueError:
                    return None
        return None

    @staticmethod
    def _compare_numeric(fact_val: Any, cond: Tuple[str, float]) -> bool:
        """Aplica comparação numérica simples entre fact_val e (op, number)."""
        try:
            fv = float(fact_val)
        except (ValueError, TypeError):
            return False
        op, num = cond
        if op == ">":
            return fv > num
        if op == ">=":
            return fv >= num
        if op == "<":
            return fv < num
        if op == "<=":
            return fv <= num
        return False

    @staticmethod
    def _time_in_range(goal_T: Any, fact_T: Any) -> bool:
        """
        Compatibilidade temporal:

        - goal_T = None        -> sempre ok
        - fact_T = None        -> fato atemporal, assume ok
        - goal_T escalar, fact_T escalar -> igualdade
        - goal_T escalar, fact_T [start,end] (end pode ser None):
            start <= goal_T <= end (ou só >= start se end None)
        - goal_T [t0,t1], fact_T [f0,f1] -> precisa interseção não vazia
        """

        if goal_T is None:
            return True
        if fact_T is None:
            return True  # fato atemporal

        def norm_interval(x):
            if isinstance(x, (list, tuple)) and len(x) == 2:
                s, e = x
                s = float(s) if s is not None else None
                e = float(e) if e is not None else None
                return s, e
            v = float(x)
            return v, v

        try:
            g0, g1 = norm_interval(goal_T)
            f0, f1 = norm_interval(fact_T)

            lo_candidates = []
            if g0 is not None:
                lo_candidates.append(g0)
            if f0 is not None:
                lo_candidates.append(f0)
            lo = max(lo_candidates) if lo_candidates else float("-inf")

            hi_candidates = []
            if g1 is not None:
                hi_candidates.append(g1)
            if f1 is not None:
                hi_candidates.append(f1)
            if not hi_candidates:
                return True
            hi = min(hi_candidates)

            return lo <= hi
        except Exception:
            return goal_T == fact_T

    @staticmethod
    def _time_leq(t1: Any, t2: Any) -> bool:
        """
        Retorna True se t1 <= t2, tratando t1 e t2 como escalares (anos).
        Se não der pra converter, retorna True (não restringe).
        """
        try:
            return float(t1) <= float(t2)
        except (ValueError, TypeError):
            return True

    # ----------------- seleção de candidatos e goals -----------------

    def _candidate_facts_for_goal(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Usa índices da KB para reduzir o número de fatos a verificar.
        Prioridade:
          - se S concreto -> by_s[S]
          - senão, se P concreto -> by_p[P]
          - senão -> todos os fatos
        """
        S = goal.get("S")
        P = goal.get("P")

        if S is not None and not self._is_var(S):
            return self.kb.by_s.get(S, [])
        if P is not None and not self._is_var(P):
            return self.kb.by_p.get(P, [])
        return self.kb.facts

    def _choose_goal_index(self, unsat: List[Dict[str, Any]]) -> int:
        """
        Escolhe qual meta em 'unsat' expandir primeiro.
        Pega aquela com menos candidatos de fatos (mais restritiva).
        """
        if not unsat:
            return 0
        best_idx = 0
        best_c = None
        for i, g in enumerate(unsat):
            c = len(self._candidate_facts_for_goal(g))
            if best_c is None or c < best_c:
                best_c = c
                best_idx = i
        return best_idx

    def _match_fact_goal(
        self,
        fact: Dict[str, Any],
        goal: Dict[str, Any],
        bindings: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Tenta casar um fato com um goal, levando em conta:
        - variáveis em qualquer campo
        - None como coringa
        - condições numéricas em O
        - compatibilidade de tempo T
        - L e C, se presentes no goal, precisam bater (ou ser variável)
        """
        new_bindings = dict(bindings)

        for key in ("S", "P", "O", "T", "L", "C"):
            gv = goal.get(key)
            fv = fact.get(key)

            if gv is None:
                continue

            if self._is_var(gv):
                unified = self._unify_var(gv, fv, new_bindings)
                if unified is None:
                    return None
                new_bindings = unified
                continue

            if key == "O":
                cond = self._parse_numeric_condition(gv)
                if cond is not None:
                    if not self._compare_numeric(fv, cond):
                        return None
                    continue
                if fv != gv:
                    return None
            elif key == "T":
                if not self._time_in_range(gv, fv):
                    return None
            else:
                if fv != gv:
                    return None

        return new_bindings

    # --------------------- Helpers para leis / exceções ---------------------

    def _fact_exists(self, S: Any, P: Any, O: Any) -> bool:
        """Verifica se existe um fato exato S,P,O no KB."""
        for f in self.kb.by_s.get(S, []):
            if f["P"] == P and f["O"] == O:
                return True
        return False

    def _law_blocked_for_case(self, lei: Any, caso: Any) -> bool:
        """
        Retorna True se houver razões explícitas pra lei NÃO se aplicar ao caso:
          - [lei, "nao_aplica_a", caso]
          - [lei, "excecao_de", condicao] E [condicao, "vale", True]
        """
        for f in self.kb.by_s.get(lei, []):
            if f["P"] == "nao_aplica_a" and f["O"] == caso:
                return True

        for f in self.kb.by_s.get(lei, []):
            if f["P"] == "excecao_de":
                cond = f["O"]
                if self._fact_exists(cond, "vale", True):
                    return True

        return False

    # --------------------------- Analogia simbólica ---------------------------

    def _similarity(self, a: Any, b: Any) -> float:
        """
        Similaridade simbólica simples baseada em fatos 'similar_a' + vizinhança.
        """
        if a == b:
            return 1.0

        sims = []
        for f in self.kb.by_s.get(a, []):
            if f["P"] == "similar_a" and f["O"] == b:
                sims.append(f["w"])
        for f in self.kb.by_s.get(b, []):
            if f["P"] == "similar_a" and f["O"] == a:
                sims.append(f["w"])

        if sims:
            return sum(sims) / len(sims)

        def neighbors(x):
            return {
                (f["P"], f["O"])
                for f in self.kb.by_s.get(x, [])
                if f["P"] not in ("similar_a",)
            }

        Na = neighbors(a)
        Nb = neighbors(b)
        if not Na or not Nb:
            return 0.0

        inter = Na & Nb
        uni = Na | Nb
        return len(inter) / len(uni)

    def _expand_analogia(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
        sim_threshold: float = 0.7,
        analog_weight_factor: float = 0.3,
    ):
        """
        Operador de analogia simbólica.

        Se queremos provar [S, P, O],
        procuramos entidades S' similares a S que tenham [S', P, O],
        e geramos um fato sintético com peso reduzido.
        """
        S = goal.get("S")
        P = goal.get("P")
        O = goal.get("O")

        if S is None or self._is_var(S):
            return
        if P is None:
            return

        for fact in self.kb.by_p.get(P, []):
            if O is not None and not self._is_var(O) and fact["O"] != O:
                continue
            Sp = fact["S"]
            sim = self._similarity(S, Sp)
            if sim < sim_threshold:
                continue

            analog_base = {
                "S": S,
                "P": P,
                "O": fact["O"],
                "T": fact.get("T"),
                "L": fact.get("L"),
                "C": fact.get("C"),
                "w": fact["w"] * analog_weight_factor * sim,
            }
            analog_fact = self._wrap_fact(analog_base, derived_by="analogico")

            new_state = {
                "unsat": remaining.copy(),
                "expl": state["expl"] + [analog_fact],
                "score": state["score"]
                + self._score_increment_for_fact(analog_fact)
                - self.complexity_penalty,
                "trace": state["trace"]
                + [("analogico", goal.copy(), fact, sim)],
                "bindings": dict(state["bindings"]),
            }
            new_states.append(new_state)

    # ---------------------- Contradições em explicações ----------------------

    def _has_contradiction(self, expl: List[Dict[str, Any]]) -> bool:
        """
        Verifica se a lista de fatos 'expl' contém pares contraditórios.
        (versão leve, direta)
        """
        so_to_ps = defaultdict(set)
        for f in expl:
            S = f.get("S")
            P = f.get("P")
            O = f.get("O")
            so_to_ps[(S, O)].add(P)

        for (S, O), preds in so_to_ps.items():
            preds_list = list(preds)
            for i in range(len(preds_list)):
                for j in range(i + 1, len(preds_list)):
                    if frozenset((preds_list[i], preds_list[j])) in self.contradictory_pairs:
                        return True
        return False

    # ----------------------- Poda de soluções dominadas ----------------------

    def _filter_dominated_solutions(self, solutions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove soluções estritamente dominadas:
        - se sol_i tem conjunto de (S,P,O) superconjunto de sol_j
          e score_i <= score_j, então sol_i é descartada.
        """
        def sig(sol):
            return {(f["S"], f["P"], f["O"]) for f in sol["expl"]}

        sols = sorted(solutions, key=lambda s: -s["score"])
        kept = []
        sigs = []

        for sol in sols:
            s_sig = sig(sol)
            dominated = False
            for best_sig, best_sol in zip(sigs, kept):
                if s_sig.issuperset(best_sig) and sol["score"] <= best_sol["score"]:
                    dominated = True
                    break
            if not dominated:
                kept.append(sol)
                sigs.append(s_sig)

        return kept

    # --------------------------- Operadores ---------------------------

    def _op_match_direct(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """Operador: match direto com fatos do KB."""
        for fact in self._candidate_facts_for_goal(goal):
            new_bindings = self._match_fact_goal(fact, goal, state["bindings"])
            if new_bindings is None:
                continue
            wrapped = self._wrap_fact(fact, derived_by="direct")
            new_state = {
                "unsat": remaining.copy(),
                "expl": state["expl"] + [wrapped],
                "score": state["score"]
                + self._score_increment_for_fact(wrapped)
                - self.complexity_penalty,
                "trace": state["trace"]
                + [("direct", goal.copy(), fact)],
                "bindings": new_bindings,
            }
            new_states.append(new_state)

    def _expand_trans_isa(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: transitividade de "é".

        (S é O?) -> se S é X e X é* O.
        """
        if goal.get("P") != "é":
            return
        if goal.get("S") is None or goal.get("O") is None:
            return

        S = goal["S"]
        O = goal["O"]
        for fact in self.kb.by_s.get(S, []):
            if fact["P"] == "é":
                mid = fact["O"]
                subgoal = {
                    "S": mid,
                    "P": "é",
                    "O": O,
                    "T": goal.get("T"),
                    "L": goal.get("L"),
                    "C": goal.get("C"),
                }
                wrapped = self._wrap_fact(fact, derived_by="trans_é")
                new_state = {
                    "unsat": [subgoal] + remaining,
                    "expl": state["expl"] + [wrapped],
                    "score": state["score"]
                    + self._score_increment_for_fact(wrapped)
                    - self.complexity_penalty,
                    "trace": state["trace"]
                    + [("trans_é", goal.copy(), fact, subgoal)],
                    "bindings": dict(state["bindings"]),
                }
                new_states.append(new_state)

    def _expand_faz_causa(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: "faz" + "pode_fazer" + "causa"

        (S faz X?) -> tente: S faz A, A causa* X, onde S pode_fazer A.
        """
        if goal.get("P") != "faz":
            return
        if goal.get("S") is None or goal.get("O") is None:
            return

        subj = goal["S"]
        target = goal["O"]
        for fact_can in self.kb.by_s.get(subj, []):
            if fact_can["P"] == "pode_fazer":
                action = fact_can["O"]
                sub1 = {"S": subj, "P": "faz", "O": action}
                sub2 = {"S": action, "P": "causa", "O": target}
                wrapped = self._wrap_fact(fact_can, derived_by="planejamento")
                new_state = {
                    "unsat": [sub1, sub2] + remaining,
                    "expl": state["expl"] + [wrapped],
                    "score": state["score"]
                    + self._score_increment_for_fact(wrapped)
                    - self.complexity_penalty,
                    "trace": state["trace"]
                    + [("faz_expand", goal.copy(), fact_can, sub1, sub2)],
                    "bindings": dict(state["bindings"]),
                }
                new_states.append(new_state)

    def _expand_causal_chain(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: encadeamento causal

        (X causa Z?) -> se X causa Y e Y causa* Z, respeitando tempo (quando houver T).
        """
        if goal.get("P") != "causa":
            return
        if goal.get("S") is None or goal.get("O") is None:
            return

        X = goal["S"]
        Z = goal["O"]
        goal_T = goal.get("T")

        for fact_c in self.kb.by_s.get(X, []):
            if fact_c["P"] != "causa":
                continue

            fact_T = fact_c.get("T")
            if goal_T is not None and fact_T is not None:
                if not self._time_leq(fact_T, goal_T):
                    continue

            mid = fact_c["O"]
            subgoal = {"S": mid, "P": "causa", "O": Z, "T": goal_T}
            wrapped = self._wrap_fact(fact_c, derived_by="causal")
            new_state = {
                "unsat": [subgoal] + remaining,
                "expl": state["expl"] + [wrapped],
                "score": state["score"]
                + self._score_increment_for_fact(wrapped)
                - self.complexity_penalty,
                "trace": state["trace"]
                + [("causa_chain", goal.copy(), fact_c, subgoal)],
                "bindings": dict(state["bindings"]),
            }
            new_states.append(new_state)

    # --------------------- Abdução: "explica" ---------------------

    def _symptoms_of(self, doenca: Any) -> List[Any]:
        """Retorna lista de sintomas associados à doença."""
        sintomas = []
        for f in self.kb.by_o.get(repr(doenca), []):
            if f["P"] in ("sintoma_de", "sintoma_tipico_de"):
                sintomas.append(f["S"])
        return sintomas

    def _expand_abducao_explica(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: abdução para 'explica'.

        goal: { "P": "explica", "O": [lista de sintomas_observados] }

        Mantém uma heurística agregada por hipótese (doença),
        não por fato individual.
        """
        if goal.get("P") != "explica":
            return
        sintomas_obs = goal.get("O")
        if not isinstance(sintomas_obs, list) or not sintomas_obs:
            return

        sintomas_obs_set = set(sintomas_obs)

        candidatos = set()
        for f in self.kb.facts:
            if f["P"] in ("sintoma_de", "sintoma_tipico_de") and f["S"] in sintomas_obs_set:
                candidatos.add(f["O"])

        if not candidatos:
            return

        alpha = 1.0
        beta = 0.5
        gamma = 0.3

        for doenca in candidatos:
            sintomas_H = set(self._symptoms_of(doenca))

            cobertos = sintomas_obs_set & sintomas_H
            tipicos_ausentes = sintomas_H - sintomas_obs_set
            nao_explicados = sintomas_obs_set - sintomas_H

            score_local = (
                alpha * len(cobertos)
                - beta * len(tipicos_ausentes)
                - gamma * len(nao_explicados)
            )

            if score_local <= 0:
                continue

            usados_wrapped: List[Dict[str, Any]] = []
            for f in self.kb.facts:
                if (
                    f["P"] in ("sintoma_de", "sintoma_tipico_de")
                    and f["O"] == doenca
                    and f["S"] in cobertos
                ):
                    # derived_by="abducao" pra entrar no esquema de operador_strength
                    base = dict(f)
                    base["w"] = score_local  # peso heurístico na hipótese
                    usados_wrapped.append(self._wrap_fact(base, derived_by="abducao"))

            delta_score = (
                sum(self._score_increment_for_fact(fw) for fw in usados_wrapped)
                - self.complexity_penalty * len(usados_wrapped)
            )

            new_state = {
                "unsat": remaining.copy(),
                "expl": state["expl"] + usados_wrapped,
                "score": state["score"] + delta_score,
                "trace": state["trace"] + [("abducao_sintomas", goal.copy(), doenca)],
                "bindings": dict(state["bindings"]),
            }
            new_states.append(new_state)

    # ------------------ "melhor_para_argumentar" (leis) --------------------

    def _is_law_valid_at(self, lei: Any, t: Any, lugar: Any = None) -> bool:
        """
        Heurística simples pra checar se uma lei está "vigente" em T.
        """
        revogacoes = [
            f for f in self.kb.by_s.get(lei, [])
            if f["P"] == "revogada_em"
        ]
        for r in revogacoes:
            try:
                trev = float(r["O"])
                tval = float(t)
                if tval >= trev:
                    return False
            except (ValueError, TypeError):
                if t == r["O"]:
                    return False

        vigencias = [
            f for f in self.kb.by_s.get(lei, [])
            if f["P"] == "vigente_em"
        ]
        if vigencias:
            for v in vigencias:
                if self._time_in_range(t, v["O"]):
                    return True
            return False

        return True

    def _score_law_for_case(
        self,
        lei: Any,
        caso: Any,
        t: Any,
        lugar: Any = None,
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Heurística de pontuação de lei para um caso em T.

        Retorna:
          (score_heuristico, [fatos_wrapped_da_lei])
        """
        if self._law_blocked_for_case(lei, caso):
            return -999.0, []

        score = 0.0
        usados_wrapped: List[Dict[str, Any]] = []

        # aplica_a direto no caso
        for f in self.kb.by_s.get(lei, []):
            if f["P"] == "aplica_a" and f["O"] == caso:
                score += 3.0
                usados_wrapped.append(self._wrap_fact(f, derived_by="lei"))

        # aplica_a em tipos do caso
        tipos_caso = [f["O"] for f in self.kb.by_s.get(caso, []) if f["P"] == "é"]
        for tipo in tipos_caso:
            for f in self.kb.by_s.get(lei, []):
                if f["P"] == "aplica_a" and f["O"] == tipo:
                    score += 2.0
                    usados_wrapped.append(self._wrap_fact(f, derived_by="lei"))

        # vigência
        if t is not None:
            if self._is_law_valid_at(lei, t, lugar=lugar):
                score += 2.0
            else:
                score -= 5.0

        # precedentes
        for f in self.kb.by_s.get(lei, []):
            if f["P"] == "precedente_favoravel" and f.get("O") in (caso, *tipos_caso):
                score += 1.5
                usados_wrapped.append(self._wrap_fact(f, derived_by="lei"))

        # conflitos
        for f in self.kb.by_s.get(lei, []):
            if f["P"] == "conflito_com":
                score -= 1.0
                usados_wrapped.append(self._wrap_fact(f, derived_by="lei"))

        return score, usados_wrapped

    def _expand_melhor_lei(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: "melhor_para_argumentar" para leis.
        """
        if goal.get("P") != "melhor_para_argumentar":
            return

        caso = goal.get("O")
        t = goal.get("T")
        lugar = goal.get("L")

        candidatos = set()
        for f in self.kb.by_p.get("aplica_a", []):
            if f["O"] == caso:
                candidatos.add(f["S"])

        tipos_caso = [f["O"] for f in self.kb.by_s.get(caso, []) if f["P"] == "é"]
        for f in self.kb.by_p.get("aplica_a", []):
            if f["O"] in tipos_caso:
                candidatos.add(f["S"])

        if not candidatos:
            for f in self.kb.by_p.get("é", []):
                if f["O"] == "lei":
                    candidatos.add(f["S"])

        for lei in candidatos:
            sc, usados_wrapped = self._score_law_for_case(lei, caso, t, lugar=lugar)
            if sc <= 0 or not usados_wrapped:
                continue

            delta_score = (
                sum(self._score_increment_for_fact(f) for f in usados_wrapped)
                - self.complexity_penalty * len(usados_wrapped)
            )

            new_state = {
                "unsat": remaining.copy(),
                "expl": state["expl"] + usados_wrapped,
                "score": state["score"] + delta_score,
                "trace": state["trace"]
                + [("melhor_lei", goal.copy(), lei, sc)],
                "bindings": dict(state["bindings"]),
            }
            s_val = goal.get("S")
            if self._is_var(s_val):
                unified = self._unify_var(s_val, lei, new_state["bindings"])
                if unified is None:
                    continue
                new_state["bindings"] = unified
            new_states.append(new_state)

    # ---------------------- Regras declarativas -----------------------------

    def _op_regras(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: aplica regras declarativas (head/body).
        """
        for rule in self.kb.rules:
            head = rule["head"]
            body = rule["body"]
            rw = rule.get("w", 1.0)
            nome = rule.get("name", "regra_anonima")

            goal_as_fact = {
                "S": goal.get("S"),
                "P": goal.get("P"),
                "O": goal.get("O"),
                "T": goal.get("T"),
                "L": goal.get("L"),
                "C": goal.get("C"),
                "w": 1.0,
            }

            new_bindings = self._match_fact_goal(goal_as_fact, head, state["bindings"])
            if new_bindings is None:
                continue

            new_unsat = list(body) + remaining

            base = {
                "S": nome,
                "P": "regra_aplicada",
                "O": repr(goal),
                "T": None,
                "L": None,
                "C": None,
                "w": rw,
            }
            rule_fact = self._wrap_fact(base, derived_by="regra")

            new_state = {
                "unsat": new_unsat,
                "expl": state["expl"] + [rule_fact],
                "score": state["score"]
                + self._score_increment_for_fact(rule_fact)
                - self.complexity_penalty,
                "trace": state["trace"]
                + [("rule", nome, head.copy(), body)],
                "bindings": new_bindings,
            }
            new_states.append(new_state)

    # ---------------------- NAF (negação como falha simples) -----------------

    def _op_naf(
        self,
        state: Dict[str, Any],
        goal: Dict[str, Any],
        remaining: List[Dict[str, Any]],
        new_states: List[Dict[str, Any]],
    ):
        """
        Operador: "nao_provavel" (negação como falha simplificada).

        Goal: { "S": x, "P": "nao_provavel", "O": "pred" }

        Lê-se: "não é provável que exista um fato (x, pred, _)", com base
        apenas na AUSÊNCIA de fatos diretos em kb.by_s[x].
        """
        if goal.get("P") != "nao_provavel":
            return

        Sg = goal.get("S")
        pred = goal.get("O")

        if Sg is None or pred is None:
            return
        if self._is_var(pred):
            return
        if pred == "nao_provavel":
            return

        # checa se existe algum fato direto (Sg, pred, _)
        existe = any(
            f["P"] == pred and f["S"] == Sg
            for f in self.kb.by_s.get(Sg, [])
        )
        if existe:
            return

        naf_base = {
            "S": Sg,
            "P": "nao_provavel",
            "O": pred,
            "T": goal.get("T"),
            "L": goal.get("L"),
            "C": goal.get("C"),
            "w": 0.1,  # bem fraco
        }
        naf_fact = self._wrap_fact(naf_base, derived_by="naf")

        new_state = {
            "unsat": remaining.copy(),
            "expl": state["expl"] + [naf_fact],
            "score": state["score"]
            + self._score_increment_for_fact(naf_fact)
            - self.complexity_penalty,
            "trace": state["trace"] + [("naf", goal.copy())],
            "bindings": dict(state["bindings"]),
        }
        new_states.append(new_state)

    # ---------------------------- Motor EXPLAIN ----------------------------

    def explain(
        self,
        goal: Dict[str, Any],
        max_depth: int = 8,
        max_solutions: int = 5,
        beam_width: int = 50,
    ) -> Dict[str, Any]:
        """
        Goal: dict com S, P, O, (T,L,C opcionais).

        Retorna:
        {
          "solutions": [estados],
          "steps": [log]
        }
        """
        initial_state = {
            "unsat": [goal],
            "expl": [],
            "score": 0.0,
            "trace": [],
            "bindings": {},
        }

        solutions: List[Dict[str, Any]] = []
        frontier: List[Dict[str, Any]] = [initial_state]
        steps_log: List[Dict[str, Any]] = []
        step_counter = 0
        seen_states = set()

        while frontier and len(solutions) < max_solutions:
            # BEAM principal: sempre pega os melhores estados atuais
            frontier.sort(key=lambda st: (-st["score"], len(st["unsat"])))
            state = frontier.pop(0)
            step_counter += 1

            key_unsat = tuple(sorted(repr(g) for g in state["unsat"]))
            key_bind = tuple(sorted(state["bindings"].items()))
            state_key = (key_unsat, key_bind)
            if state_key in seen_states:
                continue
            seen_states.add(state_key)

            steps_log.append(
                {
                    "step": step_counter,
                    "unsat": state["unsat"].copy(),
                    "score": state["score"],
                    "bindings": dict(state["bindings"]),
                }
            )

            if not state["unsat"]:
                solutions.append(state)
                continue

            if len(state["expl"]) >= max_depth:
                continue

            goal_index = self._choose_goal_index(state["unsat"])
            raw_goal = state["unsat"][goal_index]
            remaining = state["unsat"][:goal_index] + state["unsat"][goal_index + 1 :]

            goal = self._apply_bindings_to_goal(raw_goal, state["bindings"])
            new_states: List[Dict[str, Any]] = []

            # aplica todos os operadores de forma uniforme, com limite por operador
            for op in self.operators:
                before = len(new_states)
                op(state, goal, remaining, new_states)
                after = len(new_states)

                limit = self.max_expansions_per_operator.get(op.__name__)
                if limit is not None and (after - before) > limit:
                    segment = new_states[before:after]
                    segment.sort(key=lambda st: (-st["score"], len(st["unsat"])))
                    segment = segment[:limit]
                    new_states[before:after] = segment

            # tira estados com contradição direta (versão leve)
            filtered_new_states = []
            for st in new_states:
                if not self._has_contradiction(st["expl"]):
                    filtered_new_states.append(st)
            new_states = filtered_new_states

            # BEAM SEARCH global
            if beam_width is not None and len(new_states) > beam_width:
                new_states.sort(key=lambda st: (-st["score"], len(st["unsat"])))
                new_states = new_states[:beam_width]

            frontier.extend(new_states)

        # poda de soluções dominadas
        solutions = self._filter_dominated_solutions(solutions)

        return {"solutions": solutions, "steps": steps_log}


# ---------------------------------------------------------
# Utilitários de debug / CLI simples
# ---------------------------------------------------------


def print_solution(sol: Dict[str, Any], idx: int):
    print(f"\n=== SOLUÇÃO #{idx} ===")
    print(f"Score: {sol['score']:.4f}")
    print("Bindings (variáveis):")
    print("  ", sol.get("bindings", {}))
    print("Explicação (fatos usados):")
    for f in sol["expl"]:
        print(f"  - {f}")
    print("Trace (como o motor pensou):")
    for t in sol["trace"]:
        print("  ", t)


def main():
    kb = KnowledgeBase()
    kb.load_json("banco.json")
    engine = BrutalEngine(kb)

    print("Motor brutal carregado com", len(kb.facts), "fatos de banco.json")
    print("Exemplos de consultas (hardcoded no main):\n")

    # Exemplo 1: dedução simples (macaco é mamifero?)
    goal1 = {"S": "macaco", "P": "é", "O": "mamifero"}
    print(">>> TESTE 1: macaco é mamifero?")
    res1 = engine.explain(goal1, max_depth=6, max_solutions=2)
    if not res1["solutions"]:
        print("  Nenhuma explicação encontrada.")
    else:
        for i, sol in enumerate(res1["solutions"], 1):
            print_solution(sol, i)

    # Exemplo 2: causal/planejamento (como eu emagreço?)
    goal2 = {"S": "eu", "P": "faz", "O": "emagrecer"}
    print("\n>>> TESTE 2: como eu emagreço?")
    res2 = engine.explain(goal2, max_depth=8, max_solutions=3)
    if not res2["solutions"]:
        print("  Nenhuma explicação encontrada.")
    else:
        for i, sol in enumerate(res2["solutions"], 1):
            print_solution(sol, i)

    # Exemplo 3: qual entidade tem altura > 120cm? (uso de variável ?x)
    goal3 = {"S": "?x", "P": "altura_cm", "O": ">120"}
    print("\n>>> TESTE 3: quais entidades têm altura_cm > 120? (variável ?x)")
    res3 = engine.explain(goal3, max_depth=4, max_solutions=10)
    if not res3["solutions"]:
        print("  Nenhuma explicação encontrada.")
    else:
        for i, sol in enumerate(res3["solutions"], 1):
            print_solution(sol, i)

    # Exemplo 4: melhor lei para argumentar no meu_caso em 2025
    goal4 = {
        "S": "?lei",
        "P": "melhor_para_argumentar",
        "O": "meu_caso",
        "T": 2025,
        "L": "brasil",
    }
    print("\n>>> TESTE 4: melhor lei para argumentar no meu_caso em 2025? (variável ?lei)")
    res4 = engine.explain(goal4, max_depth=6, max_solutions=3)
    if not res4["solutions"]:
        print("  Nenhuma explicação encontrada.")
    else:
        for i, sol in enumerate(res4["solutions"], 1):
            print_solution(sol, i)

    print("\nEdite o main() ou chame engine.explain(goal) do jeito que quiser.")


if __name__ == "__main__":
    main()
