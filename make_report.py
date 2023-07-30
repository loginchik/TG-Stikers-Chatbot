from db_operations import stickers_db, daily_db, date_func


def collect_stats() -> str:
    stickers_sent_today = daily_db.get_stickers_send(day=date_func.todays_date())
    total_packs = stickers_db.count_sets()
    
    report_text = f'REPORT\n\nStickers sent today: {stickers_sent_today}\nTotal sets count: {total_packs}'
    return report_text


filepaths = ['logs/activity.log', 'logs/db.log', 'logs/improvements.log']
filenames = [f'ActivityLog{date_func.todays_date()}.log', f'DBLog{date_func.todays_date()}.log', f'ImprovementLog{date_func.todays_date()}.log']
file_captions = ['Activity logs', 'Database logs', 'Improvements logs']