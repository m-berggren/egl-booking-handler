from dataclasses import dataclass, field
import itertools
from typing import List

import parser.functions


@dataclass
class UnitType:
    container_count_list: List = field(default_factory=list)
    net_weight_list: List = field(default_factory=list)
    tare_weight_list: List = field(default_factory=list)
    hazards_list: List = field(default_factory=list)

    def concatenate_floats(self, *lists: list) -> float:
        concatenated_list = itertools.chain.from_iterable(*lists)
        summa = float(sum(concatenated_list))
        return int(summa)

    def calculate_weights(self) -> float:
        container_amount = self.concatenate_floats(self.container_count_list)
        if container_amount == 0:
            return 0.00
        else:
            return (float(self.concatenate_floats(self.net_weight_list)) / container_amount)

    def calculate_vgm(self):
        return round(
            (
                self.calculate_weights(self.net_weight_list, self.container_count_list)
                + self.calculate_weights(
                    self.tare_weight_list, self.container_count_list
                )
            )
        )

    def create_hazards_list(self) -> str:
        def concatenate_list(*lists):
            return itertools.chain.from_iterable(*lists)

        unique_list = concatenate_list(self.hazards_list)
        return " ".join(set(unique_list)).replace("//", "")
