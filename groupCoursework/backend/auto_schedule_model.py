from ortools.sat.python import cp_model

def ShiftDayScheduler(min_employees, max_employees, all_days, employees_to_availability, min_segments, max_segments):
    model = cp_model.CpModel()

    '''
    #min and max employees working at the same time
    min_employees = 2
    max_employees = 4

    # day = index, index = opening times
    days_to_segments = [16,16,16,16,8]
    all_days = []
    for day in days_to_segments:
        all_days.append(range(day)) 

    # employee = index, index[0] = min_segments, index[1] = max_segments
    employees_to_availability = [[20,30],[20,30],[0,30],[0,30],[0,30],[0,30],[0,30],[0,30],[0,30],[0,30]]
    
    #min and max shift durations
    min_segments = 5
    max_segments = 9
    '''
    
    shifts = {}
    #for employee in all_employees:
    for employee_num, employee in enumerate(employees_to_availability):
        for day_num, day in enumerate(all_days):
            for segment_num, segment in enumerate(day):
                shifts[(employee_num, day_num, segment_num)] = model.NewBoolVar('shift_employee%iday%isegment%i' % (employee_num, day_num, segment_num))
    
    for day_num, day in enumerate(all_days):
        for segment_num, segment in enumerate(day):
            model.Add(sum(shifts[(employee_num, day_num, segment_num)]  for employee_num, employee in enumerate(employees_to_availability)) >= min_employees)
            model.Add(max_employees >= sum(shifts[(employee_num, day_num, segment_num)] for employee_num, employee in enumerate(employees_to_availability)))


    for employee_num, employee in enumerate(employees_to_availability):
        total_segments_worked = []
        for day_num, day in enumerate(all_days):
            segments_worked = []
            for segment_num, segment in enumerate(day):
                #Check for direct segment availability
                if(segment[employee_num]):
                    segments_worked.append(shifts[(employee_num, day_num, segment_num)])
                    total_segments_worked.append(shifts[(employee_num, day_num, segment_num)])
                else:
                    model.Add(shifts[employee_num,day_num,segment_num] == 0)
                #model.AddBoolOr(segment[employee_num]) #TESTOIGMNklhdghkjs
            #reject segments under min_segments
            for length in range(1, min_segments):
                for start in range(len(segments_worked) - length + 1):
                    model.AddBoolOr(negated_bounded_span(segments_worked, start, length))
            #reject segments over max_segments
            for start in range(len(segments_worked) - max_segments):
                model.AddBoolOr([segments_worked[i].Not() for i in range(start, start + max_segments + 1)])
            
            #daily max segments
            model.Add(sum(segments_worked) <= max_segments)

        #weekly max segments
        model.Add(employee[0] <= sum(total_segments_worked))
        model.Add(sum(total_segments_worked) <= employee[1])
        

    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    #solver.parameters.num_search_workers = 1
    #solver.parameters.log_search_progress = True

    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True

    class EmployeePartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""

        def __init__(self, shifts, num_employees, all_days, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_employees = num_employees
            self._all_days = all_days
            self._solution_count = 0
            self._solution_limit = limit
            self._solutions = []

        def on_solution_callback(self):
            self._solution_count += 1
            data = []
            print('\nSolution %i' % self._solution_count)
            for day_num, day in enumerate(all_days):
                data.append([])
                #print('Day %i' % day_num)
                for employee in range(self._num_employees):
                    data[day_num].append([])
                    is_working = False
                    for segment_num, segment in enumerate(day):
                        if self.Value(self._shifts[(employee, day_num, segment_num)]):
                            data[day_num][employee].append(True)
                            is_working = True
                            #print('  Employee %i works segment_num %i' % (employee, segment_num))
                        else:
                            data[day_num][employee].append(False)
                    #if not is_working:
                        #print('  Employee {} does not work'.format(employee))

            self.pretty_print_data(data)
            self._solutions.append(data)
            if self._solution_count >= self._solution_limit:
                print('Stop search after %i solutions' % self._solution_limit)
                self.StopSearch()

        def solution_count(self):
            return self._solution_count

        def get_solutions(self):
            return self._solutions

        def pretty_print_data(self, data):
            for day_num, day in enumerate(data):
                print("\nDay: {}".format(day_num))
                print("---------------")
                segment_line = "    Segment: "
                segments = len(day[0])
                for i in range(segments):
                    if (i < 10):
                        segment_line = segment_line + str(i) + "  "
                    else:
                        segment_line = segment_line + str(i) + " "
                print(segment_line)
                for employee_num, employee in enumerate(day):
                    if (employee_num < 10):
                        employee_line = " Employee {}:".format(employee_num)
                    else:
                        employee_line = "Employee {}:".format(employee_num)
                    for segment in employee:
                        if (segment):
                            employee_line = "{} x ".format(employee_line)
                        else:
                            employee_line = "{} - ".format(employee_line)
                    print(employee_line)

    # Display the first x solutions. (Doesn't seem to work lol)
    solution_limit = 5
    solution_printer = EmployeePartialSolutionPrinter(shifts, len(employees_to_availability), all_days,
                                                solution_limit)
    solver.Solve(model, solution_printer)

    # Statistics.
    print('\nStatistics')
    print('  - conflicts      : %i' % solver.NumConflicts())
    print('  - branches       : %i' % solver.NumBranches())
    print('  - wall time      : %f s' % solver.WallTime())
    print('  - solutions found: %i' % solution_printer.solution_count())
    
    return solution_printer.get_solutions()


def negated_bounded_span(segments_worked, start, length):
    sequence = []
    # Left border (start of segments_worked, or segments_worked[start - 1])
    if start > 0:
        sequence.append(segments_worked[start - 1])
    for i in range(length):
        sequence.append(segments_worked[start + i].Not())
    # Right border (end of segments_worked or segments_worked[start + length])
    if start + length < len(segments_worked):
        sequence.append(segments_worked[start + length])
    return sequence
