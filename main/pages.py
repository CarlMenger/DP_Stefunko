from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class FirstSort(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "first_sort"

    def is_displayed(self):
        return self.round_number == 1


class ReverseSort(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "reverse_sort"

    def is_displayed(self):
        return self.round_number == 2


class InstructionsControl(Page):
    form_model = "player"

    def is_displayed(self):
        return self.session.config["treatment"] == 0 and self.round_number == 1

    def vars_for_template(self):
        return dict(fixed_payment=int(self.session.config["fixed_payment"]),
                    treatment=self.session.config["treatment"],
                    )


class ExperimentControl(Page):
    form_model = "player"
    form_fields = ["roll"]

    def is_displayed(self):
        return self.session.config["treatment"] == 0

    # def get_form_fields(self):
    #     if self.player.firstA:
    #         return ["exp_choiceA"]
    #     else:
    #         return ["exp_choiceB"]

    def vars_for_template(self):
        return dict(round=self.round_number
                    )


class InstructionsBts(Page):
    form_model = "player"
    form_fields = ["check_question", ]

    def is_displayed(self):
        return self.session.config["treatment"] == 1

    def vars_for_template(self):
        return dict(additional_payment=int(self.session.config["additional_payment"]),
                    fixed_payment=int(self.session.config["fixed_payment"]),
                    )


class ExperimentBts(Page):
    form_model = "player"

    # form_fields = ["exp_choiceA", "exp_choiceB", ]

    def is_displayed(self):
        return self.session.config["treatment"] == 1

    def vars_for_template(self):
        return dict(additional_payment=int(self.session.config["additional_payment"]),
                    fixed_payment=int(self.session.config["fixed_payment"]),
                    round=self.round_number,
                    treatment=self.session.config["treatment"],
                    firstA=self.player.firstA,
                    )

    def get_form_fields(self):
        return ["roll", "predict_1", "predict_2", "predict_3", "predict_4", "predict_5", "predict_6", ]


class CalcScores(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "calculate_scores"


class Questionnaire(Page):
    form_model = "player"
    form_fields = ["male", "nationality", "faculty"]

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        return dict(
            result1=self.player.in_round(1).result,
            result2=self.player.in_round(2).result,
            top30_1=self.player.in_round(1).top30,
            top30_2=self.player.in_round(2).top30,
            treatment=self.session.config["treatment"],
            additional_payment=int(self.session.config["additional_payment"]),
            # fixed_payment=self.session.config["fixed_payment"],
            final_payment=self.player.payoff,
        )


class Results(Page):
    def vars_for_template(self):
        return dict(
            firstA=self.player.firstA,
            additional_payment=int(self.session.config["additional_payment"]),
            treatment=self.session.config["treatment"],
            round=self.round_number,
            result=self.player.result,
            top30=self.player.top30,
            roll=self.player.roll,
        )


page_sequence = [
    # one of Instructions
    InstructionsControl,
    InstructionsBts,

    # Sort into roles
    FirstSort,
    ReverseSort,

    # Rounds
    ExperimentControl,
    ExperimentBts,

    # Post round scores calculation and display
    CalcScores,
    Results,

    # Final results + questionnaire
    Questionnaire,
]
