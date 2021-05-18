from logic import *
import itertools as itertools


def test_1():
    rain = Fact("rain")
    sun = Fact("sun")
    not_sun = Fact("sun", False)

    case1 = Case(0.5, [not_sun, rain])
    case2 = Case(0.5, [sun])

    case_model = CaseModel(cases=[case1, case2])
    assert case_model.valid

    argument = Argument(premises=[rain], conclusions=[not_sun])
    assert argument.is_coherent_in(case_model)
    assert argument.is_conclusive_in(case_model)


def test_proof_with_and_without_probabilities():
    punishment = Fact("punishment", True)
    no_punishment = Fact("punishment", False)
    guilt = Fact("guilt", True)
    no_guilt = Fact("guilt", False)
    evidence = Fact("evidence", True)
    no_evidence = Fact("evidence", False)
    justification = Fact("justification", True)
    alibi = Fact("alibi", True)

    case1 = Case(0.50, [punishment, guilt, evidence])
    case2 = Case(0.25, [no_punishment, guilt, evidence, justification])
    case3 = Case(0.25, [no_guilt, evidence, alibi])
    case_model = CaseModel(cases=[case1, case2, case3])
    assert case_model.valid

    argument1 = Argument([evidence], [guilt])
    argument2 = Argument([guilt], [punishment])
    argument3 = Argument([evidence], [guilt, punishment])
    argument4 = Argument([evidence, alibi], [guilt])
    argument5 = Argument([guilt, justification], [punishment])
    argument6 = Argument([evidence, alibi], [guilt, punishment])
    argument7 = Argument([evidence, justification], [guilt, punishment])
    argument8 = Argument([evidence, justification], [guilt])
    assert argument1.is_presumptively_valid_in(case_model)
    assert argument2.is_presumptively_valid_in(case_model)
    assert argument3.is_presumptively_valid_in(case_model)
    assert not argument4.is_presumptively_valid_in(case_model)
    assert not argument5.is_presumptively_valid_in(case_model)
    assert not argument6.is_presumptively_valid_in(case_model)
    assert not argument7.is_presumptively_valid_in(case_model)
    assert argument8.is_presumptively_valid_in(case_model)


def test_simonshaven_simplified() -> None:
    # =============================
    # === Simplified Case Model ===
    # ===       page 1179       ===
    # =============================
    guilty = Fact("guilty")
    robbery = Fact("robbery")
    perry = Fact("Perry")
    third = Fact("third")
    all_evidence = Fact("all evidence")

    not_guilty = Fact("guilty", False)
    not_robbery = Fact("robbery", False)
    not_perry = Fact("Perry", False)
    not_all_evidence = Fact("all evidence", False)

    case1 = Case(0.5, [guilty, all_evidence])
    case2_a = Case(0.2, [guilty, robbery, perry, not_all_evidence])
    case2_b = Case(0.2, [not_guilty, robbery, not_perry, third, not_all_evidence])
    case3 = Case(0.1, [not_guilty, not_robbery, not_all_evidence])

    simplified_case_model = CaseModel(cases=[case1, case2_a, case2_b, case3])

    assert simplified_case_model.valid

    # Examples from Simonshaven paper, section 2.2.1 - Arguments

    argument1 = Argument(premises=[all_evidence], conclusions=[guilty])
    assert argument1.is_coherent_in(simplified_case_model)
    assert argument1.is_conclusive_in(simplified_case_model)

    argument2 = Argument(premises=[all_evidence], conclusions=[perry])
    assert not argument2.is_coherent_in(simplified_case_model)
    assert not argument2.is_conclusive_in(simplified_case_model)

    # Presumptive Validity
    argument3 = Argument(premises=[], conclusions=[guilty])
    assert argument3.is_coherent_in(simplified_case_model)
    assert argument3.is_presumptively_valid_in(simplified_case_model)
    assert not argument3.is_conclusive_in(simplified_case_model)

    argument4 = Argument(premises=[], conclusions=[perry])
    assert argument4.is_coherent_in(simplified_case_model)
    assert not argument4.is_presumptively_valid_in(simplified_case_model)
    assert not argument4.is_conclusive_in(simplified_case_model)
    


def test_simonshaven_full() -> None:
    # =======================
    # === Full Case Model ===
    # ===    page 191     ===
    # =======================
    # GUILT: victim-killed ∧ guilt ∧ hit-by-gun ∧ hit-by-suspect ∧ motive
    GUILT = [
        Fact("victim-killed"),
        Fact("guilt"),
        Fact("hit-by-gun"),
        Fact("hit-by-suspect"),
        Fact("motive"),
    ]
    # PERRY: victim-killed ∧ ¬guilt ∧ robbery ∧ perry
    PERRY = [
        Fact("victim-killed"),
        Fact("guilt", False),
        Fact("robbery"),
        Fact("perry"),
    ]
    # THIRD: victim-killed ∧ ¬guilt ∧ robbery ∧ ¬perry ∧ third
    THIRD = [
        Fact("victim-killed"),
        Fact("guilt", False),
        Fact("robbery"),
        Fact("perry", False),
        Fact("third"),
    ]
    # OTHER: victim-killed ∧ ¬guilt ∧ ¬robbery
    OTHER = [Fact("victim-killed"), Fact("guilt", False), Fact("robbery", False)]

    # EVIDENCE: suspect-with-spatters ∧ suspect-with-wound ∧ suspect-shaking ∧ remains-victim ∧
    # victim-bloody-face ∧ pool-of-blood ∧ neck-injury ∧ cartridges ∧ gunshot-residue-victim ∧
    # v-shaped-wounds ∧ gunshot-residue-suspect ∧ past-threats ∧ past-violence ∧ separation ∧
    # dating-other-men ∧ statement-suspect ∧ pit-found ∧ no-long-stay ∧ denial ∧ no-match-perry ∧
    # no-fit-pipe ∧ phone-not-linked ∧ no-match-description ∧ dna-unknown-third ∧ sound-in-bushes ∧
    # no-connection ∧ delayed-emergency-call ∧ gunshot-residue ∧ cigarette-butts ∧ says-walking ∧
    # seen-in-car ∧ saw-nothing-special ∧ wounds-and-blood ∧ says-robbed ∧ valuables-not-stolen ∧
    # remains-silent
    EVIDENCE = [
        Fact("suspect-with-splatters"),
        Fact("suspect-with-wound"),
        Fact("suspect-shaking"),
        Fact("remains-victim"),
        Fact("victim-bloody-face"),
        Fact("pool-of-blood"),
        Fact("neck-injury"),
        Fact("cartridges"),
        Fact("gunshot-residue-victim"),
        Fact("v-shaped-wounds"),
        Fact("gunshot-residue-suspect"),
        Fact("past-threats"),
        Fact("past-violence"),
        Fact("separation"),
        Fact("dating-other-men"),
        Fact("statement-suspect"),
        Fact("pit-found"),
        Fact("no-long-stay"),
        Fact("denial"),
        Fact("no-match-perry"),
        Fact("no-fit-pipe"),
        Fact("phone-not-linked"),
        Fact("no-match-description"),
        Fact("dna-unknown-third"),
        Fact("sound-in-bushes"),
        Fact("no-connection"),
        Fact("delayed-emergency-call"),
        Fact("gunshot-residue"),
        Fact("cigarette-butts"),
        Fact("says-walking"),
        Fact("seen-in-car"),
        Fact("saw-nothing-special"),
        Fact("wounds-and-blood"),
        Fact("says-robbed"),
        Fact("valuables-not-stolen"),
        Fact("remains-silent"),
    ]

    # Case 1, Case 3, Case 2.1, ..., Case 2.5, Case 4.1, ..., Case 4.7, respectively: 50 %, 20 %, 4 %, ..., 4 %, 1.4 %, ..., 1.4 %.
    case_1 = Case(facts=GUILT + EVIDENCE, probability=0.5)

    case_2_1 = Case(
        facts=PERRY + EVIDENCE[:16] + [Fact("no-long-stay", False)], probability=0.04
    )
    case_2_2 = Case(
        facts=PERRY + EVIDENCE[:18] + [Fact("no-match-perry", False)], probability=0.04
    )
    case_2_3 = Case(
        facts=PERRY + EVIDENCE[:19] + [Fact("no-fit-pipe", False)], probability=0.04
    )
    case_2_4 = Case(
        facts=PERRY + EVIDENCE[:20] + [Fact("phone-not-linked", False)],
        probability=0.04,
    )
    case_2_5 = Case(
        facts=PERRY + EVIDENCE[:21] + [Fact("no-match-description", False)],
        probability=0.04,
    )
    case_3 = Case(
        facts=THIRD + EVIDENCE[:24] + [Fact("no-connection", False)], probability=0.2
    )
    case_4_1 = Case(
        facts=OTHER + EVIDENCE[:25] + [Fact("delayed-emergency-call", False)],
        probability=0.014,
    )
    case_4_2 = Case(
        facts=OTHER + EVIDENCE[:26] + [Fact("gunshot-residue", False)],
        probability=0.014,
    )
    case_4_3 = Case(
        facts=OTHER + EVIDENCE[:27] + [Fact("cigarette-butts", False)],
        probability=0.014,
    )
    # TODO:make sure the "Or" is correctly used
    case_4_4 = Case(
        facts=OTHER
        + EVIDENCE[:28]
        + [Fact("says-walking", False), Fact("seen-in-car", False)],
        probability=0.014,
    )
    case_4_5 = Case(
        facts=OTHER
        + EVIDENCE[:30]
        + [Fact("saw-nothing-special", False), Fact("wounds-and-blood", False)],
        probability=0.014,
    )
    case_4_6 = Case(
        facts=OTHER
        + EVIDENCE[:32]
        + [Fact("says-robbed", False), Fact("valuables-not-stolen", False)],
        probability=0.014,
    )
    case_4_7 = Case(
        facts=OTHER + EVIDENCE[:34] + [Fact("remains-silent", False)], probability=0.014
    )

    full_case_model = CaseModel(
        [
            case_1,
            case_3,
            case_2_1,
            case_2_2,
            case_2_3,
            case_2_4,
            case_2_5,
            case_4_1,
            case_4_2,
            case_4_3,
            case_4_4,
            case_4_5,
            case_4_6,
            case_4_7,
        ]
    )

    assert full_case_model.valid

    # Arguments (page 1192)

    argument_1 = Argument(
        premises=[Fact("remains-victim")], conclusions=[Fact("victim-killed")]
    )
    # By Case 1
    assert argument_1.is_coherent_in(full_case_model)
    # Since Case 1 in maximal in the ordering
    assert argument_1.is_presumptively_valid_in(full_case_model)
    # Since all cases imply 'victim-killed'
    assert argument_1.is_conclusive_in(full_case_model)

    argument_2 = Argument(premises=[Fact("pit-found")], conclusions=[Fact("perry")])
    assert argument_2.is_coherent_in(full_case_model)  # Eg. by Case 2
    # Case 1 is higher in the ordering, implying 'pit-found' but not 'perry'
    assert not argument_2.is_presumptively_valid_in(full_case_model)
    # Cases 1 and 3 imply that 'pit-found' does not imply 'perry'
    assert not argument_2.is_conclusive_in(full_case_model)

    # Argument 3 premises: EVIDENCE[from 'pit-found' until 'no-match-description']
    argument_3 = Argument(premises=EVIDENCE[16:22], conclusions=[Fact("perry")])
    # No cases imply the extended premises and the conclusion
    assert not argument_3.is_coherent_in(full_case_model)
