
# E.g. 12:20 actual time, and start time: 13:40
min_hour = 13
actual_hour = 12
actual_minute = 20
menetrend = {'start_minute': 40}

remained_minute = ((min_hour - actual_hour) - 1) * 60  + (60 - actual_minute) +  menetrend['start_minute']

assert remained_minute == 80, f'Expected 80 but got {remained_minute}'

print(f'Remained minute: {remained_minute}')
# Output: Remained minute: 80
# Explanation:
# From 12:20 to 13:00 = 40 minutes
# From 13:00 to 13:40 = 40 minutes
# Total = 40 + 40 = 80 minutes
# The formula calculates the total minutes remaining until the start time.



# Now: 13:20
actual_hour = 13
actual_minute = 20
menetrend = {'start_minute': 40}
jaratsuruseg = 15  # Every 15 minutes
min_hour = 13
max_hour = 15
# arrive: 13:40,13:55,14:10,14:25,14:40,14:55,15:10


def calculate_next_arrival(actual_hour, actual_minute, menetrend, jaratsuruseg, min_hour, max_hour, expected_remained_minute):
    calculate_arrive_hour = min_hour  # It should be arrive in this hour or later
    calculate_arrive_minute = menetrend['start_minute']
    while calculate_arrive_hour <= actual_hour and calculate_arrive_minute < actual_minute:
        # Step until the 'latest'
        calculate_arrive_minute += jaratsuruseg
        while calculate_arrive_minute >= 60:
            calculate_arrive_hour += 1
            calculate_arrive_minute -= 60
    # Here we have the calculated first next arrive
    #                  hour diff                                 # Until the end of this hour    # Remained minutes in the latest (arriving) hour
    if calculate_arrive_hour > actual_hour:
        remained_minute = ((calculate_arrive_hour - actual_hour)-1) * 60 + (60 - actual_minute) + calculate_arrive_minute
    else:
        remained_minute = calculate_arrive_minute - actual_minute

    assert remained_minute == expected_remained_minute, f'Expected {expected_remained_minute} but got {remained_minute}'
    print(f'Remained minute: {remained_minute}')
    # Output: Remained minute: 20
    # Explanation:
    # From 13:20 to 14:00 = 40 minutes

    # aktuál óra: 13
    # aktuál perc: 20
    # menetrend: első indulás:40

# Now: 13:20
actual_hour = 13
actual_minute = 20
menetrend = {'start_minute': 40}
jaratsuruseg = 15  # Every 15 minutes
min_hour = 13
max_hour = 15
# arrive: 13:40,13:55,14:10,14:25,14:40,14:55,15:10
expected_remained_minute = 20

calculate_next_arrival(actual_hour, actual_minute, menetrend, jaratsuruseg, min_hour, max_hour, expected_remained_minute)


# Now: 13:40
actual_hour = 13
actual_minute = 40
menetrend = {'start_minute': 40}
jaratsuruseg = 40  # Every 15 minutes
min_hour = 13
max_hour = 15
# arrive: 13:40 (old), 14:20,15:00
expected_remained_minute = 0

calculate_next_arrival(actual_hour, actual_minute, menetrend, jaratsuruseg, min_hour, max_hour, expected_remained_minute)


# Now: 13:40
actual_hour = 13
actual_minute = 41
menetrend = {'start_minute': 40}
jaratsuruseg = 40  # Every 15 minutes
min_hour = 13
max_hour = 15
# arrive: 13:40 (old), 14:20,15:00
expected_remained_minute = 39

calculate_next_arrival(actual_hour, actual_minute, menetrend, jaratsuruseg, min_hour, max_hour, expected_remained_minute)

