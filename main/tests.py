from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants
from otree.api import Submission
import random
import numpy


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            if self.participant.session.config["treatment"] == 0:
                yield pages.InstructionsControl,
            else:
                yield pages.InstructionsBts, dict(check_question=True)

        # Rounds
        if self.participant.session.config["treatment"] == 0:
            yield pages.ExperimentControl, dict(roll=2)
            # yield pages.ExperimentControl, dict(roll=int(*random.sample([1, 2, 3, 4, 5, 6], 1)))
        # Make sum of predictions for player equal 100 %
        lottery = []
        upper = 100
        for i in range(5):
            lottery.append(random.randrange(0, upper))
            upper -= lottery[-1]
        lottery.append(100 - sum(lottery))
        random.shuffle(lottery)
        if self.participant.session.config["treatment"] == 1:
            yield pages.ExperimentBts, dict(roll=int(*random.sample([1, 2, 3, 4, 5, 6], 1)),
                                            # roll=2,
                                            predict_1=lottery[0],
                                            predict_2=lottery[1],
                                            predict_3=lottery[2],
                                            predict_4=lottery[3],
                                            predict_5=lottery[4],
                                            predict_6=lottery[5],
                                            )

        yield pages.Results,
        # Final results + questionnaire
        if self.round_number == 2:
            yield pages.Questionnaire, dict(age=random.randint(18, 124),
                                            male=str(*random.sample([True, False], 1)),
                                            nationality=str(*random.sample(["svk", "czk", "other"], 1)),
                                            faculty=str(*random.sample(
                                                ["LF", "FaF", "FF", "PrF", "FSS", "PriF", "FI", "PdF", "FSpS", "ESF", ],
                                                1))
                                            ),
            # yield pages.LastPage,
