"""
Core data models and utilities for Cuphead boss keystroke logging.
"""
import json
import csv
import time
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
import yaml


@dataclass
class FightSession:
    """Represents a single boss fight session."""
    fight_id: str
    boss: str
    loadout: str
    difficulty: str
    start_utc: str
    start_time_ms: float
    
    @classmethod
    def create_new(cls, boss: str, loadout: str, difficulty: str = "Regular") -> 'FightSession':
        """Create a new fight session with generated ID and current timestamp."""
        now_utc = datetime.now(timezone.utc)
        start_utc_str = now_utc.isoformat().replace(':', '-').replace('+00:00', 'Z')
        
        # Generate a unique fight ID with timestamp and random component
        fight_id = f"{start_utc_str}_{uuid.uuid4().hex[:8]}"
        
        return cls(
            fight_id=fight_id,
            boss=boss,
            loadout=loadout,
            difficulty=difficulty,
            start_utc=now_utc.isoformat(),
            start_time_ms=time.perf_counter() * 1000
        )


@dataclass
class KeyEvent:
    """Represents a keyboard event during gameplay."""
    fight_id: str
    event: str  # "keydown" or "keyup"
    key: str
    t_ms: int  # milliseconds since fight start


@dataclass
class FightSummary:
    """Represents the outcome and summary of a fight."""
    fight_id: str
    outcome: str  # "win" or "lose"
    duration_ms: int
    end_utc: str
    n_events: int


class DataLogger:
    """Handles writing JSONL files and CSV summaries."""
    
    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)
        self.raw_dir = self.data_root / "raw"
        self.summaries_dir = self.data_root / "summaries"
        
        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
    
    def start_fight(self, session: FightSession) -> Path:
        """Start a new fight and write the metadata line."""
        jsonl_path = self.raw_dir / f"{session.fight_id}.jsonl"
        
        meta_record = {
            "fight_id": session.fight_id,
            "meta": {
                "boss": session.boss,
                "loadout": session.loadout,
                "difficulty": session.difficulty,
                "start_utc": session.start_utc
            }
        }
        
        with open(jsonl_path, 'w') as f:
            f.write(json.dumps(meta_record) + '\n')
            f.flush()
        
        return jsonl_path
    
    def log_event(self, event: KeyEvent, jsonl_path: Path):
        """Log a single keyboard event to the JSONL file."""
        event_record = {
            "fight_id": event.fight_id,
            "event": event.event,
            "key": event.key,
            "t_ms": event.t_ms
        }
        
        with open(jsonl_path, 'a') as f:
            f.write(json.dumps(event_record) + '\n')
            f.flush()
    
    def end_fight(self, summary: FightSummary, jsonl_path: Path, session: FightSession):
        """Write the fight summary to both JSONL and CSV."""
        # Write summary to JSONL
        summary_record = {
            "fight_id": summary.fight_id,
            "summary": {
                "outcome": summary.outcome,
                "duration_ms": summary.duration_ms,
                "end_utc": summary.end_utc
            }
        }
        
        with open(jsonl_path, 'a') as f:
            f.write(json.dumps(summary_record) + '\n')
            f.flush()
        
        # Write to CSV summary
        csv_path = self.summaries_dir / "fight_summaries.csv"
        
        # Check if CSV exists and has header
        csv_exists = csv_path.exists()
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write header if file is new or empty
            if not csv_exists or csv_path.stat().st_size == 0:
                writer.writerow([
                    'fight_id', 'boss', 'loadout', 'difficulty', 
                    'outcome', 'duration_s', 'n_events', 'recorded_utc'
                ])
            
            writer.writerow([
                summary.fight_id,
                session.boss,
                session.loadout,
                session.difficulty,
                summary.outcome,
                round(summary.duration_ms / 1000, 2),  # Convert to seconds
                summary.n_events,
                summary.end_utc
            ])


class Config:
    """Configuration loader and manager."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or use defaults."""
        default_config = {
            'difficulty': 'Regular',
            'loadout': 'Peashooter + Smoke Bomb',
            'bosses': [
                'Cagney Carnation',
                'Baroness Von Bon Bon', 
                'Grim Matchstick',
                'Glumstone the Giant'
            ],
            'hotkeys': {
                'start': 'F1',
                'end': 'F2',
                'lose': 'F8',
                'win': 'F9'
            },
            'log': {
                'write_mode': 'append',
                'flush_every_event': True
            },
            'qa': {
                'min_duration_s': 10,
                'min_events': 30
            }
        }
        
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(loaded_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return default_config
    
    @property
    def bosses(self):
        return self.config['bosses']
    
    @property
    def default_loadout(self):
        return self.config['loadout']
    
    @property
    def default_difficulty(self):
        return self.config['difficulty']
    
    @property
    def hotkeys(self):
        return self.config['hotkeys']
    
    @property
    def qa_settings(self):
        return self.config['qa']