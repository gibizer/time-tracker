from typing import List, Optional, Dict, Set

import copy
import json
import enum
import datetime
import collections
import logging
import math
import itertools

LOG = logging.getLogger(__name__)

class Task:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    @classmethod
    def from_primitive(cls, primitive):
        return Task(**primitive)

    def to_primitive(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Tasks:
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks

    @classmethod
    def from_primitive(cls, primitive) -> "Tasks":
        return Tasks([Task.from_primitive(task) for task in primitive])

    def create_one(self, name) -> Task:
        task = Task(id=self._next_id(), name=name)
        self.tasks.append(task)
        return task

    def _next_id(self) -> int:
        if not self.tasks:
            return 0

        return max([task.id for task in self.tasks]) + 1

    def get_by_id(self, id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == id:
                return task
        return None

    def to_primitive(self):
        return [task.to_primitive() for task in self.tasks]

class Action(enum.Enum):
    START = 1
    STOP = 2

class Activity:
    def __init__(self, id: int, task_id: int, action: Action, at: str):
        self.id = id
        self.task_id = task_id
        self.action = action
        self.at = at

    @classmethod
    def from_primitive(cls, primitive):
        primitive["action"] = Action(primitive["action"])
        return Activity(**primitive)

    def to_primitive(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "action": self.action.value,
            "at": self.at,
        }

class Activities:
    def __init__(self, activities: List[Activity]):
        self.activities = activities

    @classmethod
    def from_primitive(cls, primitive) -> "Activities":
        return Activities([Activity.from_primitive(act) for act in primitive])

    def to_primitive(self):
        return [activity.to_primitive() for activity in self.activities]

    def create_one(self, task_id: int, action: Action) -> Activity:
        at = datetime.datetime.now().isoformat()
        activity = Activity(
            id=self._next_id(), task_id=task_id, action=action, at=at)
        self.activities.append(activity)
        return activity

    def _next_id(self) -> int:
        if not self.activities:
            return 0

        return max([activity.id for activity in self.activities]) + 1

    def get_activities_by_task_id(self) -> Dict[int, List[Activity]]:
        act_by_task_id = collections.defaultdict(list)
        for act in self.activities:
            act_by_task_id[act.task_id].append(act)
        return act_by_task_id

    def get_active_task_id(self) -> Optional[int]:
        act_by_task_id = self.get_activities_by_task_id()

        def is_active(acts: List[Activity]):
            if not acts:
                return False
            return acts[-1].action == Action.START

        active_task_ids = [
            id for id, acts in act_by_task_id.items() if is_active(acts)]

        if len(active_task_ids) > 1:
            LOG.warning(
                "Multiple active tasks %s, using most recent one.",
                str(active_task_ids))

        if not active_task_ids:
            return None

        return active_task_ids[0]

    def get_task_runtime(self, task_id):
        return self.filter_by_task(task_id).get_runtime()

    def filter_by_day(self, day: datetime.date) -> "Activities":
        daily_activities = [
            a for a in self.activities
            if datetime.datetime.fromisoformat(a.at).date() == day
            ]
        return Activities(daily_activities)

    def filter_by_task(self, task_id: int) -> "Activities":
        return Activities([a for a in self.activities if a.task_id == task_id])

    def get_runtime(self) -> datetime.timedelta:
        acts = copy.deepcopy(self.activities)
        if len(acts) % 2 == 1:
            # A task is active, calculate with the current time as end time
            acts.append(
                Activity(
                    -1,
                    self.get_active_task_id(),
                    Action.STOP,
                    at=datetime.datetime.now().isoformat()
                    )
                )

        runtime = datetime.timedelta()
        for start, stop in itertools.batched(acts, n=2):
            runtime += (
                datetime.datetime.fromisoformat(stop.at)
                - datetime.datetime.fromisoformat(start.at))

        return runtime

    def __iter__(self):
        for a in self.activities:
            yield a

    def __getitem__(self, i):
        return self.activities[i]

    def __len__(self):
        return len(self.activities)


class TasksView:
    def __init__(self, tasks: Tasks, activities: Activities):
        self.tasks = tasks
        self.activities = activities


    def get_data(self):
        data = []
        active_task_id = self.activities.get_active_task_id()
        acts_by_task_id = self.activities.get_activities_by_task_id()

        for task in self.tasks.tasks:
            d = {
                "id": task.id,
                "name": task.name,
                "state": "running" if task.id == active_task_id else "stopped",
                "runtime": str(self.activities.get_task_runtime(task.id)),
                "changes": len(acts_by_task_id[task.id]),
            }
            data.append(d)

        return data

    @classmethod
    def get_columns(cls):
        return ["name", "state", "runtime", "changes"]

class DailyWorkSummaryView:
    def __init__(self, tasks: Tasks, daily_activities: Activities):
        self.tasks = tasks
        self.activities = daily_activities

    def get_nr_of_ctx_switches(self):
        return math.floor(len(self.activities) / 2)

    def get_start_time(self) -> datetime.datetime:
        if len(self.activities) == 0:
            return None

        return datetime.datetime.fromisoformat(self.activities[0].at)

    def get_end_time(self) -> datetime.datetime:
        if len(self.activities) == 0:
            return None

        return datetime.datetime.fromisoformat(self.activities[-1].at)

    def get_total_time(self) -> datetime.timedelta:
        return self.activities.get_runtime()

    def get_activated_task_names(self) -> Set[str]:
        return {self.tasks.get_by_id(a.task_id).name for a in self.activities}


class DailyWorkSummaryTableView:
    def __init__(self, tasks: Tasks, activities: Activities, nr_of_days: int):
        day = datetime.date.today()
        self.daily_sums: List[DailyWorkSummaryView] = []
        self.days : List[datetime.date]= []
        for _ in range(nr_of_days):
            if day.weekday() == 5: # saturday
                day = day - datetime.timedelta(days=1) # move back to friday
            if day.weekday() == 6: # sunday
                day = day - datetime.timedelta(days=2) # move back to friday

            daily_acts = activities.filter_by_day(day)
            if not daily_acts:
                continue # skip empty days

            self.days.append(day)
            self.daily_sums.append(
                DailyWorkSummaryView(tasks, activities.filter_by_day(day)))

            day = day - datetime.timedelta(days=1)


    @classmethod
    def get_columns(cls):
        return [
            "day", "start", "end", "total", "active tasks", "context switches"]

    def get_data(self):
        data = []
        for day, sum in zip(self.days, self.daily_sums):
            day_ = day.strftime("%m.%d. %A")
            start = sum.get_start_time().strftime("%H:%M:%S")
            end = sum.get_end_time().strftime("%H:%M:%S")
            # round to seconds precision for display
            total = str(datetime.timedelta(
                seconds=math.floor(sum.get_total_time().total_seconds())))

            tasks = sorted(
                sum.get_activated_task_names(), key=lambda v: v.lower())

            data.append({
                "day": day_,
                "start": start,
                "end": end,
                "total": total,
                "active tasks": str(len(tasks)) + ": " +  ", ".join(tasks),
                "context switches": sum.get_nr_of_ctx_switches(),
            })
        return data



class Controller:
    def __init__(self):
        with open("tasks.json", 'r') as fp:
            self.tasks = Tasks.from_primitive(json.load(fp))

        with open("activities.json", 'r') as fp:
            self.activities = Activities.from_primitive(json.load(fp))

    def get_tasks_view(self) -> TasksView:
        return TasksView(self.tasks, self.activities)

    def change_task_state(self, task_id):
        active_task_id = self.activities.get_active_task_id()
        if task_id == active_task_id:
            self.stop_task(task_id)
        elif active_task_id is None:
            self.start_task(task_id)
        else:
            self.stop_task(active_task_id)
            self.start_task(task_id)

        self.save()

    def stop_task(self, task_id):
        LOG.info("Stopping task '%s'", self.tasks.get_by_id(task_id).name)
        self.activities.create_one(task_id, Action.STOP)

    def start_task(self, task_id):
        LOG.info("Starting task '%s'", self.tasks.get_by_id(task_id).name)
        self.activities.create_one(task_id, Action.START)

    def save(self):
        with open("tasks.json", "w") as fp:
            json.dump(self.tasks.to_primitive(), fp, indent=2)

        with open("activities.json", "w") as fp:
            json.dump(self.activities.to_primitive(), fp, indent=2)

    def get_daily_summary_table(
        self,
        days_back: int
    ) -> DailyWorkSummaryTableView:
        return DailyWorkSummaryTableView(
            self.tasks, self.activities, days_back)