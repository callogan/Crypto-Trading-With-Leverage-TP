import csv
import os
import logging
from datetime import datetime
from typing import Dict, Any

class CSVWriter:
    def __init__(self):
        self.csv_file = self._setup_csv_file()
        
    def _setup_csv_file(self) -> str:
        """Setup CSV file for recording trade results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"trade_results_{timestamp}.csv"

        # Create directory if it doesn't exist
        os.makedirs('trade_results', exist_ok=True)
        csv_path = os.path.join('trade_results', csv_filename)

        # Write CSV header
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'wallet', 'direction', 'size', 'status',
                'active_branches', 'thread_count', 'transaction_hash', 'error'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        logging.info(f"Created CSV file for trade results: {csv_path}")
        return csv_path

    def record_trade(self, trade_data: Dict[str, Any]):
        """Record trade result to CSV file"""
        with open(self.csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'timestamp', 'wallet', 'direction', 'size', 'status',
                'active_branches', 'thread_count', 'transaction_hash', 'error'
            ])
            writer.writerow(trade_data)
            logging.info(f"Recorded trade result to CSV: {trade_data}") 