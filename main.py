"""Entry point for the CLI Alarm Clock application.

Architecture overview
---------------------
AlarmService   – business logic: add / delete / snooze / match alarms
AlarmDao       – JSON persistence layer
AlarmScheduler – background thread that polls every second and fires alarms
BeepService    – daemon thread that plays terminal bell sounds

The scheduler runs in a daemon thread so it exits automatically when the main
thread ends. User input is collected in the main thread and routed to the
appropriate service or scheduler method.
"""

import threading

from services.alarm_scheduler import AlarmScheduler
from services.alarm_service import AlarmService
from services.sound_service import BeepService


def show_menu():
    """Print the main menu to stdout."""
    print("\n===== Alarm Clock =====")
    print("1. Add Alarm")
    print("2. List Alarms")
    print("3. Delete Alarm")
    print("4. Exit")
    print("(s/d when alarm is ringing to Snooze / Dismiss)")


def main():
    """Bootstrap services, start the scheduler thread, and run the input loop."""
    alarm_service = AlarmService()
    beep_service = BeepService()
    scheduler = AlarmScheduler(alarm_service, beep_service)

    scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
    scheduler_thread.start()

    while True:
        show_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            time_str = input("Enter time (HH:MM): ").strip()
            date_str = input("Enter date (DD/MM/YYYY): ").strip()
            daily = input("Daily? (y/n): ").strip().lower() == "y"
            try:
                alarm = alarm_service.add_new_alarm(time=time_str, date=date_str, daily=daily)
                print(f"Alarm added (ID {alarm.id}).")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            alarms = alarm_service.get_all_alarms()
            if not alarms:
                print("No active alarms.")
            for alarm in alarms:
                repeat = "daily" if alarm.daily else alarm.date
                print(f"  ID={alarm.id}  TIME={alarm.time}  REPEAT={repeat}")

        elif choice == "3":
            try:
                alarm_id = int(input("Alarm ID to delete: ").strip())
                alarm_service.delete_alarm(alarm_id)
                print("Alarm deleted.")
            except ValueError:
                print("Error: please enter a numeric ID.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":
            scheduler.stop()
            print("Goodbye.")
            break

        elif choice == "s":
            if scheduler.get_current_alarm() is None:
                print("No alarm is currently ringing.")
            else:
                scheduler.snooze_alarm()
                print(f"Snoozed for {AlarmScheduler.SNOOZE_MINUTES} minutes.")

        elif choice == "d":
            if scheduler.get_current_alarm() is None:
                print("No alarm is currently ringing.")
            else:
                scheduler.dismiss_alarm()
                print("Alarm dismissed.")

        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
