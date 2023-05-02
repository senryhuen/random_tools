import argparse
from datetime import timedelta
import icalendar


def parse_ics_file(file_path):
    """Parses an iCalendar file and returns a list of events."""
    with open(file_path, "rb") as f:
        cal = icalendar.Calendar.from_ical(f.read())

    events = []
    for event in cal.walk("VEVENT"):
        events.append(
            {
                "summary": event.get("summary"),
                "start_time": event.get("dtstart").dt,
                "end_time": event.get("dtend").dt,
                "location": event.get("location"),
                "description": event.get("description"),
            }
        )

    return events


def write_events_to_file(events, file_path):
    """
    Writes a list of events to a text file in a human-readable format.

    Format:
        Title/Summary
        YYYY/MM/DD Z - YYYY/MM/DD Z (Duration)

    """
    dt_fmt = "%Y/%m/%d %H:%M:%S %Z"

    with open(file_path, "w") as f:
        for event in events:
            start_time_str = event["start_time"].strftime(dt_fmt)
            end_time_str = event["end_time"].strftime(dt_fmt)
            duration = event["end_time"] - event["start_time"]
            duration_str = str(timedelta(seconds=duration.total_seconds()))

            f.write(f'{event["summary"]}\n')
            f.write(f"{start_time_str} - {end_time_str} ({duration_str})\n")

            if event["location"]:
                f.write(f'Location: {event["location"]}\n')

            if event["description"]:
                f.write(f'Description: {event["description"]}\n')

            f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Parse an ICS file and create a human-readable text file."
    )

    parser.add_argument("input_file", help="filepath to the input ICS file")
    parser.add_argument("output_file", help="filepath for the output text file")
    args = parser.parse_args()

    events = parse_ics_file(args.input_file)
    write_events_to_file(events, args.output_file)

    print(f"{len(events)} events written to {args.output_file}.")


if __name__ == "__main__":
    main()
