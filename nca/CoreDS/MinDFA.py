#
# Copyright 2020- IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#
from greenery import fsm, parse, charclass
from functools import lru_cache


# TODO: consider adding abstract base class for MinDFA and CanonicalIntervalSet , with common api


class Alphabet:
    default_dfa_alphabet_chars = ".\\w/\\-"
    default_alphabet_regex = "[.\\w/\\-]*"
    all_charclasses = set()

    def __init__(self):
        return

    @staticmethod
    def all_charclasses_set():
        if len(Alphabet.all_charclasses) > 0:
            return Alphabet.all_charclasses
        f = parse(Alphabet.default_alphabet_regex).to_fsm()
        # for canonical rep -- transform to minimal MinDFA
        f.reduce()
        res = MinDFA.dfa_from_fsm(f)
        # res = MinDFA.dfa_from_regex(Alphabet.default_alphabet_regex)
        s = res.fsm.strings([])
        c_set = set()
        i = 0
        while i < 200:
            str_val = next(s)
            if len(str_val) > 1:
                break
            # print(str_val)
            c_set.add(charclass.Charclass(str_val))
            i += 1
        Alphabet.all_charclasses = c_set
        return Alphabet.all_charclasses


class MinDFA:
    """
    MinDFA is a wrapper class for greenery.fsm , to support the api required for dimensions in hypercube-set
    (similar to CanonicalIntervalSet)
    It holds an fsm object of type greenery.fsm, and has the following additional members:
    - is_all_words: flag (ternary-logic) to indicate if it is known for this DFA if its language is all words or not.
    - complement_dfa: either None (if complement dfa is unknown) or another MinDFA object which complements this
                      dfa to all words.

    Assumptions:
    (1) assuming that all MinDFA objects are originated from dfa_from_regex(), or dfa_from_fsm() on fsm that
        is originated from MinDFA (or operations between two fsms originated from MinDFA)
    (2) Based on (1), assuming that two MinDFA objects are equal iff they have the exact same set of states
       (including states numbers), same initial state, same final states, and same transition relation.
       This is because in greenery.fsm, the fsm construction is deterministic (see fsm.crawl() )

    (3) thus, for performance considerations, overriding the __eq__ method, and adding the __hash__ function.
        MinDFA comparison is more lightweight this way , rather than using fsm.equivalent() method.

    (4) assuming that any comparison or other operations between two MinDFA objects, are for DFAs of the same
       alphabet.
      In MinDFA __eq__ and __hash__ ignoring the alphabet: for performance considerations, allowing to build MinDFA with
      a minimal relevant alphabet (e.g. alphabet for "PUT" is {P,U,T,everything_else})
      * for a DFA originated from finite-len language of regexp, the alphabet will be restricted to the words' alphabet.
      * for a DFA of an infinite language, it will necessarily have the original alphabet.
        that is because, in istio, regexp with * is always translated to: [any allowed char]*
        and relevant also for the complement case, since we subtract from (dfa_all_words).
      * assuming that no finite-len DFA MinDFA any char that is illegal in the original alphabet.(legal input only)

    (5) assuming that all operations between MinDFA objects are with respect to a common dimension
        (no mix of MinDFA objects from different dimensions context)

    """
    default_dfa_alphabet_chars = ".\\w/\\-"
    default_alphabet_regex = "[.\\w/\\-]*"

    class Ternary:
        FALSE = 0
        TRUE = 1
        UNKNOWN = 2

    def __init__(self, alphabet, states, initial, finals, map):
        """
        create a new MinDFA object.
        input params - as described in greenery.fsm
        additional members:
        is_all_words: flag to indicate (when possible) if the DFA is equal to the entire domain
                     (e.g. create from_fsm dfa_all_words)
                     Relevant for performance improvements (though, if keeping the current __eq__ override, may not be
                                                            necessary)
        complement_dfa: MinDFA of the complement dfa of self, e.g: relevant when doing subtraction from 'all'.
                        for performance improvement (avoid computation of complement if could use this member instead).

        regex_expr: str representation of regex expressions (possibly) with operations (subtract/intersect/union),
                    from which the MinDFA object was constructed
        """
        self.fsm = fsm.Fsm(initial=initial, finals=finals, alphabet=alphabet, states=states, map=map)
        self.is_all_words = MinDFA.Ternary.UNKNOWN
        self.complement_dfa = None
        self.regex_expr = ''

    def __contains__(self, string):
        return string in self.fsm

    @staticmethod
    def dfa_from_fsm(f):
        """
        create MinDFA object from a greenery.fsm object
        :param  fsm.Fsm  f: the input fsm, assuming f was reduced (min fsm)
        :return: MinDFA object
        """
        return MinDFA(f.alphabet, f.states, f.initial, f.finals, f.map)

    # TODO: verify it is canonical rep for minDFA (except alphabet) (also for __hash__)
    def __eq__(self, other):
        if not isinstance(other, MinDFA):
            return False
        # [s1, o1] = fsm.unify_alphabets((self.fsm, other.fsm))
        # s1.reduce()
        # o1.reduce()
        # states_eq = s1.states == o1.states
        # initial_eq = s1.initial == o1.initial
        # finals_eq = s1.finals == o1.finals
        # map_eq = s1.map == o1.map
        # if not map_eq:
        #     for k in s1.map:
        #         if s1.map[k] != o1.map[k]:
        #             print('debug')

        # res = s1.states == o1.states and s1.initial == o1.initial and \
        #       s1.finals == o1.finals and s1.map == o1.map
        res = self.fsm.states == other.fsm.states and self.fsm.initial == other.fsm.initial and \
              self.fsm.finals == other.fsm.finals and self.fsm.map == other.fsm.map

        return res

    def __ne__(self, other):
        return not self == other

    def convert_to_unique_alphabet(self):
        partition = fsm.repartition(Alphabet.all_charclasses_set() | self.fsm.alphabet)
        self.fsm = self.fsm.replace_alphabet(partition)

    @staticmethod
    # TODO: currently not using the alphabet input param, due to the assumptions above.
    #  If not having these assumptions, and using DFA comparison from fsm.equivalence(), then
    #  when not being used from DFA_all_words, should provide alphabet set
    #  (for MinDFA equivalence in canonical rep, need to have the same alphabet for equal DFAs)
    @lru_cache(maxsize=500)
    def dfa_from_regex(s, alphabet=None):
        """
        Using greenery to convert regex to a minimal (canonical) DFA
        :param str s: the input regular expression
        :param str alphabet: (optional) the alphabet for the required output DFA
        :return: MinDFA object, with language equivalent to the input's regex language
        """
        # TODO: consider runtime impact for using alphabet...
        # alphabet = None
        # f = parse(s).to_fsm(alphabet)
        f = parse(s).to_fsm()
        # for canonical rep -- transform to minimal MinDFA
        f.reduce()
        res = MinDFA.dfa_from_fsm(f)
        res.convert_to_unique_alphabet()
        res.rebuild_unique_dfa()
        # TODO: currently assuming input str as regex only has '*' operator for infinity
        if '*' not in s:
            res.is_all_words = MinDFA.Ternary.FALSE
        res.regex_expr = s.replace(MinDFA.default_alphabet_regex, "*")
        return res

    @staticmethod
    def dfa_all_words(alphabet):
        """
        get MinDFA for all words in a domain
        :param str alphabet: regular expression for all words in a domain
        :return: MinDFA object such that its language is equivalent to all words in the domain
        """
        res = MinDFA.dfa_from_regex(alphabet)
        res.is_all_words = MinDFA.Ternary.TRUE
        res.regex_expr = '*'
        return res

    # TODO: this function may not be necessary, if keeping the current __eq__ override
    def is_dfa_wll_words(self, all_words_dfa):
        """
        return True iff self is equivalent to DFA of all words.
        avoid dfa-comparison if possible (rely on is_all_words and len() when possible )
        :param MinDFA all_words_dfa: the DFA of all words for the relevant domain.
        :rtype: bool
        """
        if self.is_all_words == MinDFA.Ternary.TRUE:
            return True
        if self.is_all_words == MinDFA.Ternary.FALSE:
            return False
        return not self.has_finite_len() and self == all_words_dfa

    def copy(self):
        # MinDFA is de-facto immutable, thus assuming copy is not used
        return NotImplemented

    def __hash__(self):
        all = MinDFA.dfa_all_words(MinDFA.default_alphabet_regex)
        [s1, o1] = fsm.unify_alphabets((self.fsm, all.fsm))
        return hash((frozenset(s1.states), frozenset(s1.finals), frozenset(s1.map), s1.initial))
        # return hash((frozenset(self.fsm.states), frozenset(self.fsm.finals), frozenset(self.fsm.map), self.fsm.initial))

    def _get_strings_set_str(self):
        """
        This method assumes that self has a finite len.
        Returns str of a set of strings with all words in the language of self.
        :rtype: str
        """
        str_values = []
        str_generator = self.fsm.strings([])
        for _ in range(0, len(self.fsm)):
            str_val = next(str_generator)
            str_val_new = ''.join(ch for ch in str_val)
            str_values.append(str_val_new)
        return ', '.join(word for word in str_values)

    def has_finite_len(self):
        """
        :return: True iff self has finite number of words accepted by it.
        :rtype: bool
        """
        if self.is_all_words == MinDFA.Ternary.TRUE:
            return False
        try:
            len(self.fsm)
            return True
        except OverflowError:
            return False

    @lru_cache(maxsize=500)
    def __str__(self):
        """
        str representation of the language accepted by this DFA:
        - option 1: if language has finite number of words -> return string with all accepted words.
        - option 2 : a string of regex expressions with accumulated operations, from which the object was constructed.
        :rtype: str
        """

        if self.has_finite_len():
            return self._get_strings_set_str()
        if self.is_all_words == MinDFA.Ternary.TRUE:
            return "*"
        return self.regex_expr
        # in comment below: alternative based on conversion from MinDFA to regex
        # not readable regex result + had performance implications of this conversion from MinDFA to regex
        # return str(from_fsm(self.fsm))

    def get_fsm_str(self):
        """
        get a string representation for this DFA from greenery.fsm str method: states and transition table.
        :rtype: str
        """
        return str(self.fsm)

    def __bool__(self):
        return not self.fsm.empty()

    def contained_in(self, other):
        """
        return True iff self is contained in other.
        :type other: minDFA
        :rtype: bool
        """
        if other.is_all_words == MinDFA.Ternary.TRUE:
            return True
        if self.is_all_words == MinDFA.Ternary.TRUE and other.is_all_words == MinDFA.Ternary.FALSE:
            return False
        # TODO: if both are finite-len, can use set containment on accepted words?
        return self.fsm.issubset(other.fsm)

    # operators within fsm already apply reduce() (minimization)
    @lru_cache(maxsize=500)
    def __or__(self, other):
        if self.is_all_words == MinDFA.Ternary.TRUE:
            return self
        if other.is_all_words == MinDFA.Ternary.TRUE:
            return other
        fsm_res = self.fsm | other.fsm
        res = MinDFA.dfa_from_fsm(fsm_res)
        if res.has_finite_len():
            res.is_all_words = MinDFA.Ternary.FALSE
        # update regex_expr of the result object
        if self.regex_expr == other.regex_expr:
            res.regex_expr = self.regex_expr
        else:
            res.regex_expr = f'({self.regex_expr})|({other.regex_expr})'
        res.rebuild_unique_dfa()
        return res

    @lru_cache(maxsize=500)
    def __and__(self, other):
        if self.is_all_words == MinDFA.Ternary.TRUE:
            return other
        if other.is_all_words == MinDFA.Ternary.TRUE:
            return self
        fsm_res = self.fsm & other.fsm
        res = MinDFA.dfa_from_fsm(fsm_res)
        if self.is_all_words == MinDFA.Ternary.FALSE or other.is_all_words == MinDFA.Ternary.FALSE:
            res.is_all_words = MinDFA.Ternary.FALSE
        # update regex_expr of the result object
        if self.regex_expr == other.regex_expr:
            res.regex_expr = self.regex_expr
        else:
            res.regex_expr = f'({self.regex_expr})&({other.regex_expr})'
        res.rebuild_unique_dfa()
        return res

    @lru_cache(maxsize=500)
    def __sub__(self, other):
        if self.is_all_words == MinDFA.Ternary.TRUE and other.complement_dfa is not None:
            return other.complement_dfa

        fsm_res = self.fsm - other.fsm
        res = MinDFA.dfa_from_fsm(fsm_res)
        # update regex_expr of the result object
        res.regex_expr = f'({self.regex_expr})-({other.regex_expr})'

        if other.is_all_words == MinDFA.Ternary.TRUE:  # res becomes empty
            res.is_all_words = MinDFA.Ternary.FALSE
        elif other:
            res.is_all_words = MinDFA.Ternary.FALSE  # res cannot be all words
        if self.is_all_words == MinDFA.Ternary.TRUE and not other:
            res.is_all_words = MinDFA.Ternary.TRUE

        if self.is_all_words == MinDFA.Ternary.TRUE:
            res.complement_dfa = other
            other.complement_dfa = res
        if res.has_finite_len():
            res.is_all_words = MinDFA.Ternary.FALSE
        res.rebuild_unique_dfa()
        return res

    @lru_cache(maxsize=500)
    def rep(self):
        """
        :return: a string accepted by this DFA
        :rtype: string
        """
        if not self:
            return NotImplemented
        str_generator = self.fsm.strings([])
        str_val = next(str_generator)
        return ''.join(ch for ch in str_val)

    def rebuild_unique_dfa(self):
        curr_map = self.fsm.map
        states_renaming = {0: 0}  # map from int to int
        states_to_visit = [0]
        visited_states = []
        next_state = 1
        while len(states_to_visit) > 0:
            curr_state = states_to_visit[0]
            states_to_visit.pop(0)
            # handle current state
            state_map_keys_sorted = sorted(list(curr_map[curr_state].keys()))
            for edge_val in state_map_keys_sorted:
                edge_state = curr_map[curr_state][edge_val]
                if not edge_state in states_renaming:
                    states_renaming[edge_state] = next_state
                    next_state += 1
                    states_to_visit.append(edge_state)
            visited_states.append(curr_state)
        new_map = dict()
        for state, state_map in curr_map.items():
            new_map[states_renaming[state]] = dict()
            for edge_val, edge_state in state_map.items():
                new_map[states_renaming[state]][edge_val] = states_renaming[edge_state]
        final_states = set(self.fsm.finals)
        final_states_new = set(states_renaming[x] for x in final_states)
        self.fsm = fsm.Fsm(initial=self.fsm.initial, finals=frozenset(final_states_new), alphabet=self.fsm.alphabet,
                           states=self.fsm.states, map=new_map)
