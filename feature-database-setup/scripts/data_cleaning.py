"""Data cleaning utilities for nfl_data_py data."""
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np
from datetime import datetime

def clean_nfl_data(data: Union[pd.DataFrame, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Clean and standardize data from nfl_data_py functions.
    
    Args:
        data: Data from nfl_data_py functions (either DataFrame or list of dicts)
        
    Returns:
        List of cleaned dictionaries ready for database insertion
    """
    if not isinstance(data, (pd.DataFrame, list)):
        raise ValueError("Input must be a pandas DataFrame or a list of dictionaries")
    
    # Convert to list of dicts if it's a DataFrame
    if isinstance(data, pd.DataFrame):
        records = data.replace({np.nan: None}).to_dict('records')
    else:
        records = data
    
    cleaned_records = []
    
    for record in records:
        cleaned = {}
        
        # Clean each field in the record
        for key, value in record.items():
            # Skip None values to avoid type conversion issues
            if value is None:
                cleaned[key] = None
                continue
                
            # Clean based on field name patterns
            if key.endswith('_id') or key in ['jersey_number', 'gsis_id']:
                # Convert ID fields to string, handling both string and numeric IDs
                cleaned[key] = str(value) if value is not None else None
                
            elif key in ['height', 'weight', 'years_exp', 'week', 'season']:
                # Convert numeric fields to int, handling None/NaN
                try:
                    cleaned[key] = int(float(value)) if value is not None and not pd.isna(value) else None
                except (ValueError, TypeError):
                    cleaned[key] = None
                    
            elif key in ['birth_date', 'game_date', 'created_at', 'updated_at']:
                # Convert date/time fields to ISO format strings
                if pd.isna(value):
                    cleaned[key] = None
                elif hasattr(value, 'isoformat'):
                    cleaned[key] = value.isoformat()
                elif isinstance(value, str):
                    cleaned[key] = value  # Assume it's already in a good format
                else:
                    cleaned[key] = None
                    
            elif key in ['status', 'position', 'team', 'conference', 'division']:
                # Convert to uppercase for consistency
                if pd.isna(value) or value is None:
                    cleaned[key] = None
                else:
                    cleaned[key] = str(value).strip().upper()
                    
            elif key.endswith('_url'):
                # Clean URL fields
                cleaned[key] = str(value).strip() if value is not None else None
                
            elif isinstance(value, (str, int, float, bool)) or value is None:
                # Pass through basic types as-is
                cleaned[key] = value
                
            else:
                # Convert any remaining types to string
                cleaned[key] = str(value) if value is not None else None
        
        cleaned_records.append(cleaned)
    
    return cleaned_records

def clean_pbp_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Clean play-by-play data from nfl_data_py.import_pbp_data().
    
    Args:
        df: DataFrame from nfl_data_py.import_pbp_data()
        
    Returns:
        List of cleaned dictionaries ready for database insertion
    """
    # Convert to list of dicts and handle NaNs
    records = df.replace({np.nan: None}).to_dict('records')
    
    # Apply standard cleaning
    cleaned = clean_nfl_data(records)
    
    # Additional PBP-specific cleaning
    for record in cleaned:
        # Ensure game_id is a string
        if 'game_id' in record and record['game_id']:
            record['game_id'] = str(record['game_id'])
            
        # Clean player IDs (can be multiple IDs separated by ';')
        for key in ['passer_player_id', 'rusher_player_id', 'receiver_player_id', 
                   'kicker_player_id', 'punter_player_id', 'returner_player_id',
                   'defender_player_id', 'tackle_with_assist_player_id', 'assist_tackle_player_id',
                   'forced_fumble_player_id', 'solo_tackle_player_id', 'tackle_with_assist_1_player_id',
                   'tackle_with_assist_2_player_id', 'assist_tackle_1_player_id', 'assist_tackle_2_player_id',
                   'forced_fumble_player_1_player_id', 'forced_fumble_player_2_player_id', 'solo_tackle_1_player_id',
                   'solo_tackle_2_player_id']:
            if key in record and record[key]:
                # Handle lists or semicolon-separated strings
                if isinstance(record[key], list):
                    record[key] = ';'.join(str(x) for x in record[key] if x)
                else:
                    record[key] = str(record[key])
    
    return cleaned

def clean_roster_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Clean roster data from nfl_data_py.import_seasonal_rosters() or import_weekly_rosters().
    
    Args:
        df: DataFrame from nfl_data_py roster functions
        
    Returns:
        List of cleaned dictionaries ready for database insertion
    """
    # Convert to list of dicts and handle NaNs
    records = df.replace({np.nan: None}).to_dict('records')
    
    # Apply standard cleaning
    cleaned = clean_nfl_data(records)
    
    # Additional roster-specific cleaning
    for record in cleaned:
        # Ensure player_id is a string
        if 'player_id' in record and record['player_id']:
            record['player_id'] = str(record['player_id'])
            
        # Clean position data
        if 'position' in record and record['position']:
            record['position'] = record['position'].strip().upper()
            
        # Clean team data
        if 'team' in record and record['team']:
            record['team'] = record['team'].strip().upper()
    
    return cleaned

def clean_ngs_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Clean Next Gen Stats data from nfl_data_py.import_ngs_data().
    
    Args:
        df: DataFrame from nfl_data_py.import_ngs_data()
        
    Returns:
        List of cleaned dictionaries ready for database insertion
    """
    # Convert to list of dicts and handle NaNs
    records = df.replace({np.nan: None}).to_dict('records')
    
    # Apply standard cleaning
    cleaned = clean_nfl_data(records)
    
    # Additional NGS-specific cleaning
    for record in cleaned:
        # Ensure player_id is a string
        if 'player_id' in record and record['player_id']:
            record['player_id'] = str(record['player_id'])
            
        # Clean team data
        if 'team_abbr' in record and record['team_abbr']:
            record['team_abbr'] = record['team_abbr'].strip().upper()
    
    return cleaned
