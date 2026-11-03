def evaluate(child):
    over = child.screen_time_minutes >= child.daily_limit_minutes
    return {"over_screen_limit": over, "should_lock": over,
            "remaining_minutes": max(0, child.daily_limit_minutes - child.screen_time_minutes),
            "daily_limit": child.daily_limit_minutes}
