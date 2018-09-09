from typing import IO, Tuple, List

# noinspection PyUnresolvedReferences,PyPackageRequirements
import sc2reader
import techlabreactor

MAX_CREEP_TUMOURS_DISPLAYED = 3
MAX_STEP_SIZE = 9
SEQUENCE_SIZE = 10
CHART_BASE_WIDTH_IN_MINUTES = 6.5
MINIMUM_MAX_UNUSED_RES = 1000
UNUSED_RES_CHART_HEIGHT = SEQUENCE_SIZE * 5
UNUSED_RES_CHART_HEIGHT_SCALE = UNUSED_RES_CHART_HEIGHT / MINIMUM_MAX_UNUSED_RES


def _frame_to_ms(frame: int, fps: int) -> int:
    return int((frame * 1000) / (1.4 * fps))


def _frame_to_seconds(frame: int, fps: int) -> int:
    return int(_frame_to_ms(frame, fps) / 1000)


def _minutes_to_frames(minutes: float, fps: int) -> int:
    return int(minutes * 60 * fps * 1.4)


def serialise_chart_data(inject_states: List[List[Tuple[int, bool]]],
                         larvae_blocks: List[List[Tuple[int, bool]]],
                         supply_blocks: List[Tuple[float, bool]],
                         creep_states_changes: List[Tuple[int, int]],
                         unused_minerals: List[Tuple[int, int]],
                         unused_gas: List[Tuple[int, int]], fps: int,
                         total_frames: int) -> list:
    chart_data = []

    offset = 0
    for injects, larvae in zip(inject_states, larvae_blocks):
        chart_data.append([[
            _frame_to_ms(frame, fps), offset + (MAX_STEP_SIZE
                                                if injected else 0)
        ] for frame, injected in injects])

        larvae_block_dataset = []
        baseline_dataset = []
        for frame, blocked in larvae:
            if blocked:
                larvae_block_dataset.append([_frame_to_ms(frame, fps), offset])
                larvae_block_dataset.append(
                    [_frame_to_ms(frame, fps), offset + MAX_STEP_SIZE])

                baseline_dataset.append([_frame_to_ms(frame, fps), offset])
                baseline_dataset.append([_frame_to_ms(frame, fps), offset])
            else:
                larvae_block_dataset.append([_frame_to_ms(frame, fps), offset])
                larvae_block_dataset.append([_frame_to_ms(frame, fps), "NaN"])

                baseline_dataset.append([_frame_to_ms(frame, fps), offset])
                baseline_dataset.append([_frame_to_ms(frame, fps), "NaN"])

        chart_data.append(larvae_block_dataset)
        chart_data.append(baseline_dataset)

        offset += SEQUENCE_SIZE

    creep_data = [[0, offset]]
    creep_state = 0
    for frame, state_change in creep_states_changes:
        creep_state += state_change
        creep_data.append([
            _frame_to_ms(frame, fps),
            offset + min(creep_state, MAX_CREEP_TUMOURS_DISPLAYED) *
            MAX_STEP_SIZE / MAX_CREEP_TUMOURS_DISPLAYED
        ])
    creep_data.append((_frame_to_ms(total_frames, fps), offset))

    chart_data.append(creep_data)

    offset += SEQUENCE_SIZE

    max_value = offset

    max_unused_res = max(MINIMUM_MAX_UNUSED_RES, max_value / UNUSED_RES_CHART_HEIGHT_SCALE)

    chart_data.append([[
        _frame_to_ms(frame, fps),
        min(minerals, max_unused_res) * UNUSED_RES_CHART_HEIGHT_SCALE
    ] for frame, minerals in unused_minerals])

    chart_data.append([[
        _frame_to_ms(frame, fps),
        min(gas, max_unused_res) * UNUSED_RES_CHART_HEIGHT_SCALE
    ] for frame, gas in unused_gas])

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


def unused_resources(
        player, replay) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    stats_events = [
        event for event in replay.tracker_events
        if event.name == "PlayerStatsEvent" and event.player == player
    ]
    return [(event.frame, event.minerals_current) for event in stats_events
            ], [(event.frame, event.vespene_current) for event in stats_events]


def analyse_replay_file(replay_name: str,
                        replay_file: IO[bytes]) -> Tuple[str, dict]:
    replay = sc2reader.SC2Reader().load_replay(replay_file)

    data = {"players": [], "replayName": replay_name}

    for player in replay.players:
        inject_states = techlabreactor.get_hatchery_inject_states_for_player(
            player, replay, 0)

        if not inject_states:
            continue

        larvae_blocks = techlabreactor.larvae_blocks_per_hatchery_for_player(
            player, replay)

        supply_blocks = techlabreactor.get_supply_blocks_till_time_for_player(
            _frame_to_seconds(replay.frames, replay.game_fps), player, replay)

        creep_states_changes = techlabreactor.creep_tumour_state_changes(
            player, replay)

        unused_minerals, unused_gas = unused_resources(player, replay)

        chart_data = serialise_chart_data(
            inject_states, larvae_blocks, supply_blocks, creep_states_changes,
            unused_minerals, unused_gas, replay.game_fps, replay.frames)

        data["players"].append({
            "chartData":
            chart_data,
            "playerName":
            player.name,
            "widthScaling":
            replay.frames / _minutes_to_frames(CHART_BASE_WIDTH_IN_MINUTES,
                                               replay.game_fps)
        })

    return replay.filehash, data
