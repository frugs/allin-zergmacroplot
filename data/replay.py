from typing import IO, Tuple, List

# noinspection PyUnresolvedReferences
import sc2reader
import techlabreactor


def _frame_to_ms(frame: int, fps: int) -> int:
    return int((frame * 1000) / (1.4 * fps))


def _frame_to_seconds(frame: int, fps: int) -> int:
    return int(_frame_to_ms(frame, fps) / 1000)


def _minutes_to_frames(minutes: float, fps: int) -> int:
    return int(minutes * 60 * fps * 1.4)


def serialise_chart_data(inject_states: List[List[Tuple[int, bool]]],
                         supply_blocks: List[Tuple[float, bool]],
                         fps: int) -> list:
    chart_data = []

    offset = 0
    for state_series in inject_states:
        chart_data.append(
            [[_frame_to_ms(frame, fps), offset + (9 if injected else 0)]
             for frame, injected in state_series])
        offset += 10

    max_value = offset

    supply_block_data = []
    was_blocked = False
    for second, blocked in supply_blocks:
        if not was_blocked and blocked:
            supply_block_data.append([int(second * 1000), 0])

        if was_blocked and not blocked:
            supply_block_data.append([int(second * 1000), 0])
            supply_block_data.append([int(second * 1000), "NaN"])

        if blocked:
            supply_block_data.append([int(second * 1000), max_value])

        was_blocked = blocked

    chart_data.append(supply_block_data)

    return chart_data


def analyse_replay_file(replay_name: str,
                        replay_file: IO[bytes]) -> Tuple[str, dict]:
    replay = sc2reader.SC2Reader().load_replay(replay_file)

    data = {"players": [], "replayName": replay_name}

    for player in replay.players:
        inject_states = techlabreactor.get_hatchery_inject_states_for_player(
            player, replay, 0)

        supply_blocks = techlabreactor.get_supply_blocks_till_time_for_player(
            _frame_to_seconds(replay.frames, replay.game_fps), player, replay)

        if not inject_states:
            continue

        chart_data = serialise_chart_data(inject_states, supply_blocks,
                                          replay.game_fps)

        data["players"].append({
            "chartData": chart_data,
            "playerName": player.name,
            "widthScaling": replay.frames / _minutes_to_frames(9, replay.game_fps)
        })

    return replay.filehash, data
