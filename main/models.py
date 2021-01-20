from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from collections import Counter
from django.contrib.postgres.fields import ArrayField
import math
import numpy as np

doc = "Decision-making experiment. \n\nControl - no info, let em cheat \n" \
      "T1 - Info with Drazen Prelecs false consensus effect"


class Constants(BaseConstants):
    name_in_url = "main"
    players_per_group = None
    num_rounds = 2
    fixed_payment = 0


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
        return bts_all[min(len(bts_all)-1, split_number)]

    # get geometrical averages of all predictions
    def geom_mean(self, predictions_matrix):
        return list(map(self.sqrt, map(self.multiply, map(list, zip(*predictions_matrix)))))

    # Needed multiplication function with unlimited arguments for map function, faster than googling build in one
    def multiply(self, *args):
        k = 1
        for i in args:
            k *= i
        return list(k)

    def sqrt(self, number: list):
        return number[0] ** (1 / len(self.get_players()))

    def counter_to_list(self, counter: Counter):
        rolls_list = [0, 0, 0, 0, 0, 0]
        for key, roll_count in counter.items():
            rolls_list[key - 1] = roll_count
        return rolls_list

    def absolute_to_relative(self, rolls: list):
        return [item / sum(rolls) for item in rolls]

    def init_predictions_matrix(self, experiment_type):
        if experiment_type == "A":
            return np.array(
                [[p.predict_1, p.predict_2, p.predict_3, p.predict_4, p.predict_5, p.predict_6] for p in
                 self.get_players() if p.firstA is True])
        elif experiment_type == "B":
            return np.array(
                [[p.predict_1, p.predict_2, p.predict_3, p.predict_4, p.predict_5, p.predict_6] for p in
                 self.get_players() if p.firstA is False])

    def laplace_transformation(self, predictions_matrix):
        participants_n = len(predictions_matrix)
        for row, player_predictions in enumerate(predictions_matrix):
            for column, prediction in enumerate(player_predictions):
                predictions_matrix[row][column] = (prediction * (participants_n - 1) + 1) / (participants_n - 1 + 6)
        return predictions_matrix

    # main loop after both rounds
    def calculate_scores(self):
        print("entered calculate_scores")

        # Count all rolls
        rolls_total_counter_A = Counter([p.roll for p in self.get_players() if p.firstA is True])
        rolls_total_counter_B = Counter([p.roll for p in self.get_players() if p.firstA is False])
        # Rolls
        for rolls in [rolls_total_counter_A, rolls_total_counter_B]:
            # Add +1 to every roll to take care of possible no rolls
            rolls.update([1, 2, 3, 4, 5, 6])
            # Transform into relative frequencies of each rolls, ordered
            rolls = self.counter_to_list(rolls)
            rolls_rel_frequency = self.absolute_to_relative(rolls)
            assert round(sum(
                rolls_rel_frequency)) == 1, f"Relative rolls count: {round(sum(rolls_rel_frequency)) * 100}% is not 100%"

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

            # geom_mean_A = list(map(self.multiply, map(list, zip(*rolls_predictions_matrix_A))))
            # geom_mean_B = list(map(self.multiply, map(list, zip(*rolls_predictions_matrix_B))))
            # print(f"Line 86: geom_mean_A: {geom_mean_A}")

            # calculate prediction score, information score and BTS for all players
            i, j = 0, 0
            for p in self.get_players():
                if p.firstA:
                    # print(f"rolls_predictions_matrix_A[i]: {rolls_predictions_matrix_A[i]}")
                    p.set_prediction_score(rolls_predictions_matrix_A[i], rolls_rel_frequency, )
                    i += 1
                    p.set_information_score(p.roll, rolls_rel_frequency, geom_mean_A)
                else:
                    p.set_prediction_score(rolls_predictions_matrix_B[j], rolls_rel_frequency, )
                    j += 1
                    p.set_information_score(p.roll, rolls_rel_frequency, geom_mean_B)
                p.bts = p.prediction_score + p.information_score

            # Do BTS leaderboard
            btsA_aggregated = sorted([p.bts for p in self.get_players() if p.firstA is True])
            btsB_aggregated = sorted([p.bts for p in self.get_players() if p.firstA is False])
            btsA_split = self.get_bts_split_value(btsA_aggregated)
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
    # predictions = ArrayField(models.FloatField(initial=0.0), size=6)
    # Roll predictions for BTS non-polarized (A)
    predict_1 = models.FloatField()
    predict_2 = models.FloatField()
    predict_3 = models.FloatField()
    predict_4 = models.FloatField()
    predict_5 = models.FloatField()
    predict_6 = models.FloatField()

    # # Roll predictions for BTS polarized (B)
    # predict_1B = models.FloatField()
    # predict_2B = models.FloatField()
    # predict_3B = models.FloatField()
    # predict_4B = models.FloatField()
    # predict_5B = models.FloatField()
    # predict_6B = models.FloatField()

    # Money earned for Exp 1 & 2
    result = models.FloatField()
    # result2 = models.FloatField()

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
        print("Vaša odpoveď", value)
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
        # log(relative_freq[roll_number] / geom_mean[roll_number]
        information_score = math.log(rolls_rel_frequency[roll_number - 1] / geom_mean[roll_number - 1])
        self.information_score = information_score
