from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from collections import Counter
import math
import numpy as np
import os

doc = "Decision-making experiment. \n\nControl - no info, let em cheat \n" \
      "T1 - Info with Drazen Prelecs false consensus effect"


class Constants(BaseConstants):
    name_in_url = "main"
    players_per_group = None
    num_rounds = 2
    fixed_payment = 0
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Subsession(BaseSubsession):
    def first_sort(self):
        split = True
        for p in self.get_players():
            p.firstA = split
            split = not split

    def reverse_sort(self):
        for p in self.get_players():
            if p.in_round(1).firstA:
                p.firstA = False
            else:
                p.firstA = True

    # value used to split BTS ladder, rounds up
    # min in index if single participant
    def get_bts_split_value(self, bts_all):
        split_number = round(len(bts_all) - (len(bts_all) / 3))
        return bts_all[min(len(bts_all) - 1, split_number)]

    # get geometrical averages of all predictions
    def geom_mean(self, predictions_matrix):
        transposed = list(map(list, zip(*predictions_matrix)))
        multiplied = [self.multiply(i) for i in transposed]
        squared = [self.sqrt(i) for i in multiplied]
        return squared
        # return list(map(self.sqrt, map(self.multiply, map(list, zip(*predictions_matrix)))))

    # Needed multiplication function with unlimited arguments for map function, faster than googling build in one
    def multiply(self, *args):
        k = 1
        for i in args[0]:
            k *= i
        return k

    def sqrt(self, number):
        return number ** (1 / len(self.get_players()))

    def counter_to_list(self, counter: Counter):
        rolls_list = [0, 0, 0, 0, 0, 0]
        for key, roll_count in counter.items():
            rolls_list[key - 1] = roll_count
        return rolls_list

    def absolute_to_relative(self, rolls: list):
        return [item / sum(rolls) for item in rolls]

    def init_predictions_matrix(self, experiment_type):
        if experiment_type == "A":
            return [[p.predict_1, p.predict_2, p.predict_3, p.predict_4, p.predict_5, p.predict_6] for p in
                    self.get_players() if p.firstA is True]
        elif experiment_type == "B":
            return [[p.predict_1, p.predict_2, p.predict_3, p.predict_4, p.predict_5, p.predict_6] for p in
                    self.get_players() if p.firstA is False]

    def laplace_transformation(self, predictions_matrix):
        participants_n = len(predictions_matrix)
        for row, player_predictions in enumerate(predictions_matrix):
            for column, prediction in enumerate(player_predictions):
                predictions_matrix[row][column] = (prediction * (participants_n - 1) + 1) / (participants_n - 1 + 6)
        return predictions_matrix

    def get_rel_frequency(self, rolls: Counter):
        rolls.update([1, 2, 3, 4, 5, 6])
        rolls = self.counter_to_list(rolls)
        rolls_rel_frequency = self.absolute_to_relative(rolls)
        assert round(sum(
            rolls_rel_frequency)) == 1, f"Relative rolls count: {round(sum(rolls_rel_frequency)) * 100}% is not 100%"
        return rolls_rel_frequency

    # main loop after both rounds
    def calculate_scores(self):
        # Count all rolls
        rolls_total_counter_A = Counter([p.roll for p in self.get_players() if p.firstA is True])
        rolls_total_counter_B = Counter([p.roll for p in self.get_players() if p.firstA is False])
        # Rolls
        rolls_rel_frequency_A = self.get_rel_frequency(rolls_total_counter_A)
        rolls_rel_frequency_B = self.get_rel_frequency(rolls_total_counter_B)

        # Predictions scores for BTS
        if self.session.config["treatment"] == 1:
            # create matrix
            rolls_predictions_matrix_A = self.init_predictions_matrix("A")
            rolls_predictions_matrix_B = self.init_predictions_matrix("B")
            # print(f"Before Laplace: rolls_predictions_matrix_A: {rolls_predictions_matrix_A}")

            # transformation to take care of 0 values
            rolls_predictions_matrix_A = self.laplace_transformation(rolls_predictions_matrix_A)
            rolls_predictions_matrix_B = self.laplace_transformation(rolls_predictions_matrix_B)

            # print(f"After Laplace: rolls_predictions_matrix_A: {rolls_predictions_matrix_A}")
            geom_mean_A = self.geom_mean(rolls_predictions_matrix_A)
            geom_mean_B = self.geom_mean(rolls_predictions_matrix_B)
            # print("geom means: ", geom_mean_A, geom_mean_B)

            # calculate prediction score, information score and BTS for all players
            i, j = 0, 0
            for p in self.get_players():
                if p.firstA:
                    # print(f"rolls_predictions_matrix_A[i]: {rolls_predictions_matrix_A[i]}")
                    p.set_prediction_score(rolls_predictions_matrix_A[i], rolls_rel_frequency_A, )
                    i += 1
                    p.set_information_score(p.roll, rolls_rel_frequency_A, geom_mean_A)
                else:
                    p.set_prediction_score(rolls_predictions_matrix_B[j], rolls_rel_frequency_B, )
                    j += 1
                    p.set_information_score(p.roll, rolls_rel_frequency_B, geom_mean_B)
                p.bts = p.prediction_score + p.information_score

            # Do BTS leaderboard
            btsA_aggregated = sorted([p.bts for p in self.get_players() if p.firstA is True])
            btsB_aggregated = sorted([p.bts for p in self.get_players() if p.firstA is False])
            if len(btsA_aggregated) > 0:
                btsA_split = self.get_bts_split_value(btsA_aggregated)
            if len(btsB_aggregated) > 0:
                btsB_split = self.get_bts_split_value(btsB_aggregated)

        for p in self.get_players():
            # Experiment A
            if p.firstA:
                if self.session.config["treatment"] == 1:
                    if p.bts >= btsA_split:
                        p.top30 = True
                p.result = p.roll + p.top30 * self.session.config["additional_payment"]
            # Experiment B
            else:
                if self.session.config["treatment"] == 1:
                    if p.bts >= btsB_split:
                        p.top30 = True
                # 1 or 6 roll == 1 KC
                if p.roll == 1 or p.roll == 6:
                    p.result = 1 + p.top30 * self.session.config["additional_payment"]
                # 2 or 5 roll == 3 KC
                elif p.roll == 1 or p.roll == 6:
                    p.result = 3 + p.top30 * self.session.config["additional_payment"]
                # 3 or 4 roll == 6 KC
                else:
                    p.result = 6 + p.top30 * self.session.config["additional_payment"]
            # Calc final payment with fixed payment this way so it shows up in admin screen
            if self.round_number == Constants.num_rounds:
                p.payoff = p.in_round(1).result + p.in_round(2).result + self.session.config["fixed_payment"]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # Roll predictions for BTS non-polarized (A)
    predict_1 = models.FloatField()
    predict_2 = models.FloatField()
    predict_3 = models.FloatField()
    predict_4 = models.FloatField()
    predict_5 = models.FloatField()
    predict_6 = models.FloatField()

    # Money earned per round
    result = models.FloatField()

    # Score predictors for BTS
    information_score = models.FloatField()
    prediction_score = models.FloatField()
    bts = models.FloatField()
    top30 = models.BooleanField(initial=False)

    # Exp order var
    firstA = models.BooleanField()

    # Instructions BTS check question
    check_question = models.BooleanField(choices=[[False, "znižuje"], [True, "zvyšuje"], [False, "nemá vplyv na"]],
                                         label="")

    # Dice Rolls
    roll = models.IntegerField(choices=[[1, "1"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"]],
                               label="Hodnota hodu:", initial=0)
    # exp_choiceA = models.IntegerField(initial=0)
    # exp_choiceB = models.IntegerField(initial=0)

    # Questionnaire
    age = models.IntegerField(label="Vek", max=123, min=18)
    male = models.BooleanField(choices=[[True, "muž"], [False, "žena"]], label="Pohlavie")
    nationality = models.StringField(choices=[["svk", "slovenská"], ["czk", "česká"], ["other", "iná"]],
                                     label="Národnosť")
    faculty = models.StringField(
        choices=[["LF", "Lékařská fakulta "], ["FaF", "Farmaceutická fakulta"], ["FF", "Filozofická fakulta"],
                 ["PrF", "Právnická fakulta "], ["FSS", "Fakulta sociálních studií "],
                 ["PriF", "Přírodovědecká fakulta "], ["FI", "Fakulta informatiky "], ["PdF", "Pedagogická fakulta "],
                 ["FSpS", "Fakulta sportovních studií"], ["ESF", "Ekonomicko-správní fakulta "]], label="Fakulta")

    def check_question_error_message(self, value):
        if not value:
            return "Zvolená odpoveď nie je správna"

    def set_prediction_score(self, predictions, rolls_rel_frequency, ):
        prediction_score = 0.0
        print("All variables for set_prediction_score")
        print(f"predictions: {predictions}"),
        print(f"rolls_rel_frequency: {rolls_rel_frequency}")
        for i in range(len(predictions)):
            prediction_score += (rolls_rel_frequency[i] * math.log(predictions[i] / rolls_rel_frequency[i]))
        self.prediction_score = prediction_score

    def set_information_score(self, roll_number, rolls_rel_frequency, geom_mean):
        # Equation log(relative_freq[roll_number] / geom_mean[roll_number]
        information_score = math.log(rolls_rel_frequency[roll_number - 1] / geom_mean[roll_number - 1])
        self.information_score = information_score
