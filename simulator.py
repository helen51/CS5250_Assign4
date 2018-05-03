'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

class Stack_Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time, stack_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.stack_time = stack_time
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d, stack_time %d]'%(self.id, self.arrive_time, self.burst_time, self.stack_time))

# def sort_list(stack_list):



def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    schedule = []
    waiting_list = []
    current_time = 0
    waiting_time = 0
    index = 0

    waiting_list.append(Stack_Process(process_list[index].id, process_list[index].arrive_time, process_list[index].burst_time, process_list[index].arrive_time))
    index += 1
    while(len(waiting_list) != 0 or index < len(process_list)):
        if(len(waiting_list) == 0):
            current_time = process_list[index].arrive_time
            waiting_list.append(Stack_Process(process_list[index].id, process_list[index].arrive_time, process_list[index].burst_time, current_time))
            index += 1
        continue_process = waiting_list.pop(0)
        if(len(schedule) == 0 or schedule[len(schedule)-1][1] != continue_process.id):
            schedule.append((current_time, continue_process.id))
        waiting_time += current_time - continue_process.stack_time
        time_count = 0
        while(time_count < continue_process.burst_time):
            if(index < len(process_list) and current_time == process_list[index].arrive_time):
                waiting_list.append(Stack_Process(process_list[index].id, process_list[index].arrive_time, process_list[index].burst_time, current_time))
                index += 1
            if(time_count >= time_quantum):
                waiting_list.append(Stack_Process(continue_process.id, continue_process.arrive_time, continue_process.burst_time - time_quantum, current_time))
                break
            else:
                time_count += 1
                current_time += 1
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    schedule = []
    waiting_list = []
    current_time = 0
    waiting_time = 0

    for process in process_list:
        index = process_list.index(process)
        next_arrive = 0
        if(index < len(process_list) - 1):
            next_arrive = process_list[index + 1].arrive_time
        while(current_time == process.arrive_time or len(waiting_list) != 0):
            if(current_time == process.arrive_time):
                waiting_list.append(Stack_Process(process.id, process.arrive_time, process.burst_time, process.arrive_time))
                waiting_list = sorted(waiting_list, key=lambda var:(var.burst_time, var.arrive_time))
            continue_process = waiting_list.pop(0)
            if(len(schedule) == 0 or schedule[len(schedule) - 1][1] != continue_process.id):
                schedule.append((current_time, continue_process.id))
            waiting_time += current_time - continue_process.stack_time
            if(next_arrive != 0):
                time_interval = next_arrive - current_time
                if(continue_process.burst_time > time_interval):
                    current_time += time_interval
                    waiting_list.append(Stack_Process(continue_process.id, continue_process.arrive_time, continue_process.burst_time - time_interval, current_time))
                    waiting_list = sorted(waiting_list, key=lambda var:(var.burst_time, var.arrive_time))
                else:
                    current_time += continue_process.burst_time
            else:
                current_time += continue_process.burst_time
            if(next_arrive != 0):
                if(len(waiting_list) == 0):
                    current_time = next_arrive
                if(current_time == next_arrive):
                    break

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SJF_scheduling(process_list, alpha):
    schedule = []
    predict_list = {}
    finished = {}
    current_time = 0
    waiting_time = 0

    for process in process_list:
        predict_list[process.id] = 5
        finished[process] = False
    
    for process in process_list:
        waiting_list = []
        for i in range(len(process_list)):
            if(current_time >= process_list[i].arrive_time and finished[process_list[i]] != True):
                waiting_list.append(process_list[i])

        if(len(waiting_list) == 0):
            current_time = process.arrive_time
            waiting_list.append(process)

        min_index = 0
        for queue_process in waiting_list:
            if(predict_list[waiting_list[min_index].id] > predict_list[queue_process.id]):
                min_index = waiting_list.index(queue_process)
        if(len(schedule) == 0 or schedule[len(schedule) - 1][1] != waiting_list[min_index].id):
            schedule.append((current_time, waiting_list[min_index].id))
        finished[waiting_list[min_index]] = True
        if(current_time >= waiting_list[min_index].arrive_time):
            waiting_time += current_time - waiting_list[min_index].arrive_time
        current_time += waiting_list[min_index].burst_time

        predict_list[waiting_list[min_index].id] = alpha * waiting_list[min_index].burst_time + (1-alpha)*predict_list[waiting_list[min_index].id]
        
        waiting_list.pop(min_index)

    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

    RR_tuning = []
    for time_quantum in range(1, 11):
        RR_schedule, rr_awt = RR_scheduling(process_list, time_quantum)
        RR_tuning.append((RR_schedule, rr_awt, time_quantum))
        print("time_quantum: %d, rr_awt: %f" % (time_quantum, rr_awt))
    RR_tuning = sorted(RR_tuning, key=lambda var: var[1])
    print(RR_tuning[0])
    write_output('RR_optimal.txt', RR_tuning[0][0], RR_tuning[0][1] )

    SJF_tuning = []
    for i in range(0, 11):
        SJF_alpha = i * 0.1
        SJF_schedule, SJF_awt =  SJF_scheduling(process_list, SJF_alpha)
        SJF_tuning.append((SJF_schedule, SJF_awt, SJF_alpha))
        print("When alpha: %f, SJF_awt: %f" % (SJF_alpha, SJF_awt))
    SJF_tuning = sorted(SJF_tuning, key=lambda var: var[1])
    print(SJF_tuning[0])
    write_output('SJF_optimal.txt', SJF_tuning[0][0], SJF_tuning[0][1] )

if __name__ == '__main__':
    main(sys.argv[1:])
