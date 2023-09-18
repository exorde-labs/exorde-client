from datetime import time, datetime


def generate_times(interval: int) -> list[time]:
    inactivity_watch_end_time: time = time(23, 59)
    current_time: time = datetime.now().time()
    inactivity_watch_start_time: time = time(0, current_time.minute)
    inactivity_watch_interval_minutes: int = 30

    times: list[time] = [
        time(
            (
                inactivity_watch_start_time.hour
                + (
                    inactivity_watch_start_time.minute
                    + inactivity_watch_interval_minutes * i
                )
                // 60
            )
            % 24,
            (
                inactivity_watch_start_time.minute
                + inactivity_watch_interval_minutes * i
            )
            % 60,
        )
        for i in range(
            (inactivity_watch_end_time.hour - inactivity_watch_start_time.hour)
            * 60
            // inactivity_watch_interval_minutes
            + 2
        )
    ]
    return times


def main():
    interval_minutes = 30
    times = generate_times(interval_minutes)

    assert len(times) == 48, f"Expected 48 elements in the list."
    # interval = 30 = 60 / 2
    # times_count = 48 = 24 * 2

    for _time in times:
        print(_time)
    print("---")

    print(times[0])
    print(times[-1])


if __name__ == "__main__":
    main()
