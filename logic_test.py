from logic import *
import itertools as itertools


def test_1():
    rain = Fact('rain')
    sun = Fact('sun')
    not_sun = Fact('sun', False)

    case1 = Case([not_sun, rain], probability=0.5, name='case1')
    case2 = Case([sun], probability=0.5, name='case2')

    case_model = CaseModel(cases=[case1, case2])

    argument = Argument(premises=[rain], conclusion=not_sun)
    coherent, coherent_case = case_model.coherent(argument)
    print('%s is coherent: %s' % (argument, coherent))
    print('%s is conclusive: %s' % (argument, case_model.conclusive(argument)))

    assert case_model.valid


def test_proof_with_and_without_probabilities():
    punishment = Fact('punishment', True)
    no_punishment = Fact('punishment', False)
    guilt = Fact('guilt', True)
    no_guilt = Fact('guilt', False)
    evidence = Fact('evidence', True)
    no_evidence = Fact('evidence', False)
    justification = Fact('justification', True)
    alibi = Fact('alibi', True)

    # (Arguments 3, 6, 7 can not be modelled properly, so there is a workaround for them.)
    case1 = Case([punishment, guilt, evidence], probability=0.50, name='case1')
    case2 = Case([no_punishment, guilt, evidence, justification], probability=0.25, name='case 2')
    case3 = Case([no_guilt, evidence, alibi], probability=0.25, name='case 3')
    case_model = CaseModel(cases=[case1, case2, case3])
    assert case_model.valid
    argument1 = Argument([evidence], guilt)
    argument2 = Argument([guilt], punishment)
    # argument3 = Argument([evidence], [guilt, punishment])
    argument3_ = Argument([evidence], punishment)
    argument4 = Argument([evidence, alibi], guilt)
    argument5 = Argument([guilt, justification], punishment)
    # argument6 = Argument([evidence, alibi], [guilt, punishment])
    argument6_ = Argument([evidence, alibi], punishment)
    # argument7 = Argument([evidence, justification], [guilt, punishment])
    argument7_ = Argument([evidence, justification], punishment)
    argument8 = Argument([evidence, justification], guilt)
    assert case_model.presumptively_valid(argument1)
    assert case_model.presumptively_valid(argument2)
    assert case_model.presumptively_valid(argument3_)
    assert not case_model.presumptively_valid(argument4)
    assert not case_model.presumptively_valid(argument5)
    assert not case_model.presumptively_valid(argument6_)
    assert not case_model.presumptively_valid(argument7_)
    assert case_model.presumptively_valid(argument8)


def test_simonshaven() -> None:
    # =============================
    # === Simplified Case Model ===
    # ===       page 1179       ===
    # =============================
    guilty = Fact('guilty')
    robbery = Fact('robbery')
    perry = Fact('Perry')
    third = Fact('third')
    all_evidence = Fact('all evidence')

    not_guilty = Fact('guilty', False)
    not_robbery = Fact('robbery', False)
    not_perry = Fact('Perry', False)
    not_all_evidence = Fact('all evidence', False)

    case1 = Case([guilty, all_evidence], probability=0.5, name='case 1')
    case2_a = Case([guilty, robbery, perry, not_all_evidence],
                   probability=0.2, name='case 2_a')
    case2_b = Case([not_guilty, robbery, not_perry, third, not_all_evidence], probability=0.2,
                   name='case2_b')
    case3 = Case([not_guilty, not_robbery, not_all_evidence],
                 probability=0.1, name='case 3')

    simplified_case_model = CaseModel(cases=[case1, case2_a, case2_b, case3])

    assert simplified_case_model.valid

    # Examples from Simonshaven paper, section 2.2.1 - Arguments
    # Coherence
    argument_coherent_conclusive = Argument(
        premises=[all_evidence], conclusion=guilty)
    print('%s is coherent: %s' % (argument_coherent_conclusive,
          simplified_case_model.coherent(argument_coherent_conclusive)))
    argument_incoherent = Argument(premises=[all_evidence], conclusion=perry)
    print('%s is coherent: %s' % (argument_incoherent,
          simplified_case_model.coherent(argument_incoherent)))

    # Presumptive Validity
    # FIXME: Not sure how to translate "from empty premises (which obtain in all cases and are logically formalized as a tautology)"
    # argument_presumptively_valid_inconclusive = Argument(premises=[Tautology()], conclusion=guilty)
    # print('%s is coherent: %s' % (argument_presumptively_valid_inconclusive, simplified_case_model.presumptively_valid(argument_presumptively_valid_inconclusive)))
    # argument_presumptively_invalid = Argument(premises=[Tautology()], conclusion=perry)
    # print('%s is coherent: %s' % (argument_presumptively_invalid, simplified_case_model.presumptively_valid(argument_presumptively_invalid)))

    # Conclusive
    print('%s is conclusive: %s' % (argument_coherent_conclusive,
          simplified_case_model.conclusive(argument_coherent_conclusive)))
    # print('%s is coherent: %s' % (argument_presumptively_valid_inconclusive, simplified_case_model.conclusive(argument_presumptively_valid_inconclusive)))

    # =======================
    # === Full Case Model ===
    # ===    page 191     ===
    # =======================
    # GUILT: victim-killed ∧ guilt ∧ hit-by-gun ∧ hit-by-suspect ∧ motive
    GUILT = [Fact("victim-killed"), Fact("guilt"),
                  Fact("hit-by-gun"), Fact("hit-by-suspect"), Fact("motive")]
    # PERRY: victim-killed ∧ ¬guilt ∧ robbery ∧ perry
    PERRY = [Fact("victim-killed"), Fact("guilt", False),
                  Fact("robbery"), Fact("perry")]
    # THIRD: victim-killed ∧ ¬guilt ∧ robbery ∧ ¬perry ∧ third
    THIRD = [Fact("victim-killed"), Fact("guilt", False),
                  Fact("robbery"), Fact("perry", False), Fact('third')]
    # OTHER: victim-killed ∧ ¬guilt ∧ ¬robbery
    OTHER = [Fact("victim-killed"), Fact("guilt", False),
                  Fact("robbery", False)]

    # EVIDENCE: suspect-with-spatters ∧ suspect-with-wound ∧ suspect-shaking ∧ remains-victim ∧
    # victim-bloody-face ∧ pool-of-blood ∧ neck-injury ∧ cartridges ∧ gunshot-residue-victim ∧
    # v-shaped-wounds ∧ gunshot-residue-suspect ∧ past-threats ∧ past-violence ∧ separation ∧
    # dating-other-men ∧ statement-suspect ∧ pit-found ∧ no-long-stay ∧ denial ∧ no-match-perry ∧
    # no-fit-pipe ∧ phone-not-linked ∧ no-match-description ∧ dna-unknown-third ∧ sound-in-bushes ∧
    # no-connection ∧ delayed-emergency-call ∧ gunshot-residue ∧ cigarette-butts ∧ says-walking ∧
    # seen-in-car ∧ saw-nothing-special ∧ wounds-and-blood ∧ says-robbed ∧ valuables-not-stolen ∧
    # remains-silent
    EVIDENCE = [Fact('suspect-with-splatters'), Fact('suspect-with-wound'), Fact('suspect-shaking'), Fact('remains-victim'),
                Fact('victim-bloody-face'), Fact('pool-of-blood'), Fact(
                    'neck-injury'), Fact('cartridges'), Fact('gunshot-residue-victim'),
                Fact('v-shaped-wounds'), Fact('gunshot-residue-suspect'), Fact(
                    'past-threats'), Fact('past-violence'), Fact('separation'),
                Fact('dating-other-men'), Fact('statement-suspect'), Fact('pit-found'), Fact(
                    'no-long-stay'), Fact('denial'), Fact('no-match-perry'),
                Fact('no-fit-pipe'), Fact('phone-not-linked'), Fact(
                    'no-match-description'), Fact('dna-unknown-third'), Fact('sound-in-bushes'),
                Fact('no-connection'), Fact('delayed-emergency-call'), Fact(
                    'gunshot-residue'), Fact('cigarette-butts'), Fact('says-walking'),
                Fact('seen-in-car'), Fact('saw-nothing-special'), Fact(
                    'wounds-and-blood'), Fact('says-robbed'), Fact('valuables-not-stolen'),
                Fact('remains-silent')]

    # Case 1, Case 3, Case 2.1, ..., Case 2.5, Case 4.1, ..., Case 4.7, respectively: 50 %, 20 %, 4 %, ..., 4 %, 1.4 %, ..., 1.4 %.
    case_1 = Case(fact_set=GUILT+EVIDENCE, probability=0.5, name='Case 1')

    case_2_1 = Case(fact_set=PERRY + EVIDENCE[:16] + [Fact(
        'no-long-stay', False)], probability=0.04, name='Case 2.1')
    case_2_2 = Case(fact_set=PERRY + EVIDENCE[:18] + [Fact(
        'no-match-perry', False)], probability=0.04, name='Case 2.2')
    case_2_3 = Case(fact_set=PERRY + EVIDENCE[:19] + [Fact(
        'no-fit-pipe', False)], probability=0.04, name='Case 2.3')
    case_2_4 = Case(fact_set=PERRY + EVIDENCE[:20] + [Fact('phone-not-linked', False)], probability=0.04,
                    name='Case 2.4')
    case_2_5 = Case(fact_set=PERRY + EVIDENCE[:21] + [Fact('no-match-description', False)], probability=0.04,
                    name='Case 2.5')

    case_3 = Case(fact_set=THIRD + EVIDENCE[:24] + [
                  Fact('no-connection', False)], probability=0.2, name='Case 3')

    case_4_1 = Case(fact_set=OTHER + EVIDENCE[:25] + [Fact('delayed-emergency-call', False)], probability=0.014,
                    name='Case 4.1')
    case_4_2 = Case(fact_set=OTHER + EVIDENCE[:26] + [Fact('gunshot-residue', False)], probability=0.014,
                    name='Case 4.2')
    case_4_3 = Case(fact_set=OTHER + EVIDENCE[:27] + [Fact('cigarette-butts', False)], probability=0.014,
                    name='Case 4.3')
    # TODO:make sure the "Or" is correctly used
    case_4_4 = Case(fact_set=OTHER + EVIDENCE[:28] + [Or(Fact('says-walking', False), Fact('seen-in-car', False))],
                    probability=0.014, name='Case 4.4')
    case_4_5 = Case(fact_set=OTHER + EVIDENCE[:30] + [Or(Fact('saw-nothing-special', False), Fact('wounds-and-blood', False))],
                    probability=0.014, name='Case 4.5')
    case_4_6 = Case(fact_set=OTHER + EVIDENCE[:32] + [Or(Fact('says-robbed', False), Fact('valuables-not-stolen', False))],
                    probability=0.014, name='Case 4.6')
    case_4_7 = Case(fact_set=OTHER + EVIDENCE[:34] + [Fact('remains-silent', False)], probability=0.014,
                    name='Case 4.7')

    full_case_model = CaseModel([case_1, case_3, case_2_1, case_2_2, case_2_3, case_2_4, case_2_5, case_4_1,
                                 case_4_2, case_4_3, case_4_4, case_4_5, case_4_6, case_4_7])

    assert full_case_model.valid

    # Arguments (page 1192)
    argument_1 = Argument(
        premises=[Fact('remains-victim')], conclusion=Fact('victim-killed'))
    assert full_case_model.coherent(argument_1)  # By Case 1
    assert full_case_model.presumptively_valid(argument_1)  # Since Case 1 in maximal in the ordering
    assert full_case_model.conclusive(argument_1)  # Since all cases imply 'victim-killed'

    argument_2 = Argument(
        premises=[Fact('pit-found')], conclusion=Fact('perry'))
    assert full_case_model.coherent(argument_2)  # Eg. by Case 2
    # Case 1 is higher in the ordering, implying 'pit-found' but not 'perry'
    assert not full_case_model.presumptively_valid(argument_2)
    # Cases 1 and 3 imply that 'pit-found' does not imply 'perry'
    assert not full_case_model.conclusive(argument_2)

    # Argument 3 premises: EVIDENCE[from 'pit-found' until 'no-match-description']
    argument_3 = Argument(premises=EVIDENCE[16:22], conclusion=Fact('perry'))
    # FIXME: This asserts the argument is coherent; paper states it's not
    # assert not full_case_model.coherent(argument_3) # No cases imply the extended premises and the conclusion

    # TODO: Should the last 3 lines of the arguments paragraph (page 1192) be done


# Make this a method of CaseModel?
# TODO: change the return (conclusion[0]) when arguments can accept many conclusions
def generate_arguments(case_model: CaseModel, conclusion: list, premise_length: int = None) -> list:
    """
    returns a list containing all possible arguments based on the given case model and the given conclusion

    :param CaseModel case_model: A case model
    :param list[Fact] conclusion: A conclusion for the argument
    :param premise_length: (Optional) The length of the arguments' premises
    :return list[Arguments]: A list of all the possible arguments
    """
    # TODO: Make sure that premise_length values are always valid
    all_cases = case_model.cases
    all_facts = [fact for case in all_cases for fact in case.fact_set]
    all_combinations = []
    if premise_length is not None:
        for subset in itertools.permutations(all_facts, premise_length):
            print(subset)
            all_combinations.append(subset)
    else:
        for length in range(0, len(all_facts)+1):
            for subset in itertools.permutations(all_facts, length):
                all_combinations.append(subset)
    return [Argument(premises=premises, conclusion=conclusion[0]) for premises in all_combinations]


if __name__ == "__main__":
    test_simonshaven()

    rain = Fact('rain')
    sun = Fact('sun')
    not_sun = Fact('sun', False)

    case1 = Case([not_sun, rain], probability=0.5, name='case1')
    case2 = Case([sun], probability=0.5, name='case2')

    case_model = CaseModel(cases=[case1, case2])

    print(generate_arguments(case_model, [not_sun]))
