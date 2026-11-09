"""Static checks for the repaired custom gift scripts (not an emulator test)."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def block(path, start_label, next_label):
    code = (ROOT / path).read_text()
    return code.split(start_label + '::', 1)[1].split(next_label + '::', 1)[0]


class GiftFlowTests(unittest.TestCase):
    def test_fossil_checks_space_and_add_result_before_flags(self):
        s = (ROOT / 'data/maps/CinnabarIsland_PokemonLab_ExperimentRoom/scripts.inc').read_text()
        for item, flag in [('HELIX_FOSSIL', 'HELIX_FOSSIL'), ('DOME_FOSSIL', 'DOME_FOSSIL')]:
            check = s.index('checkitemspace ITEM_' + item)
            add = s.index('additem ITEM_' + item, check)
            failure = s.index('goto_if_eq VAR_RESULT, FALSE, CinnabarIsland_PokemonLab_ExperimentRoom_EventScript_SecondFossilNoRoom', add)
            ownflag = s.index('setflag FLAG_GOT_' + flag, failure)
            self.assertTrue(check < add < failure < ownflag)
        self.assertIn('setflag FLAG_PLG_SECOND_FOSSIL_GIFT', s)

    def test_celio_tickets_have_same_transactional_flow(self):
        s = (ROOT / 'data/maps/OneIsland_PokemonCenter_1F/scripts.inc').read_text()
        for item, code, flag in [('MYSTIC_TICKET', 'NAVEL_ROCK', 'MYSTIC_TICKET'), ('AURORA_TICKET', 'BIRTH_ISLAND', 'AURORA_TICKET')]:
            check = s.index('checkitemspace ITEM_' + item)
            add = s.index('additem ITEM_' + item, check)
            failure = s.index('goto_if_eq VAR_RESULT, FALSE, OneIsland_PokemonCenter_1F_EventScript_PLG_TicketNoRoom', add)
            shipflag = s.index('setflag FLAG_ENABLE_SHIP_' + code, failure)
            giftflag = s.index('setflag FLAG_PLG_GOT_' + flag, shipflag)
            self.assertLess(check, add)
            self.assertLess(add, failure)
            self.assertLess(failure, shipflag)
            self.assertLess(shipflag, giftflag)
            self.assertIn('checkitem ITEM_' + item + ', 1', s)
        no_room = block('data/maps/OneIsland_PokemonCenter_1F/scripts.inc',
                        'OneIsland_PokemonCenter_1F_EventScript_PLG_TicketNoRoom',
                        'OneIsland_PokemonCenter_1F_EventScript_PLG_TicketEnd')
        self.assertNotIn('setflag', no_room)

    def test_obsolete_partial_patch_removed(self):
        self.assertFalse((ROOT / 'LeafGreen_reward_flow_fix.patch').exists())


if __name__ == '__main__':
    unittest.main()
