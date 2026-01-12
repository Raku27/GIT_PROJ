"""
Data Validation Script for Hotel Analysis
Validates data quality and integrity
"""

import pandas as pd
import numpy as np
from datetime import datetime


class HotelDataValidator:
    """Class for validating hotel data quality"""
    
    def __init__(self, data_path):
        """
        Initialize the validator
        
        Args:
            data_path (str): Path to the data file
        """
        self.data_path = data_path
        self.df = None
        self.validation_results = {}
        
    def load_data(self):
        """Load data for validation"""
        try:
            if self.data_path.endswith('.csv'):
                self.df = pd.read_csv(self.data_path)
            elif self.data_path.endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(self.data_path)
            
            print(f"Data loaded for validation: {len(self.df)} rows")
            return self.df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            raise
    
    def check_missing_values(self):
        """Check for missing values"""
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        
        result = pd.DataFrame({
            'column': missing.index,
            'missing_count': missing.values,
            'missing_percentage': missing_pct.values
        })
        result = result[result['missing_count'] > 0].sort_values('missing_count', ascending=False)
        
        self.validation_results['missing_values'] = result
        print(f"\nMissing Values Check:")
        print(result.to_string(index=False))
        return result
    
    def check_duplicates(self):
        """Check for duplicate records"""
        duplicate_count = self.df.duplicated().sum()
        duplicate_pct = (duplicate_count / len(self.df)) * 100
        
        self.validation_results['duplicates'] = {
            'count': duplicate_count,
            'percentage': duplicate_pct
        }
        
        print(f"\nDuplicate Check:")
        print(f"Duplicate records: {duplicate_count} ({duplicate_pct:.2f}%)")
        return duplicate_count
    
    def check_data_types(self):
        """Check data types"""
        dtype_info = pd.DataFrame({
            'column': self.df.columns,
            'dtype': self.df.dtypes,
            'non_null_count': self.df.count().values
        })
        
        self.validation_results['data_types'] = dtype_info
        print(f"\nData Types:")
        print(dtype_info.to_string(index=False))
        return dtype_info
    
    def check_value_ranges(self):
        """Check for outliers and invalid values"""
        issues = []
        
        # Check numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if 'revenue' in col.lower() or 'rate' in col.lower():
                # Revenue/rate should be positive
                negative_count = (self.df[col] < 0).sum()
                if negative_count > 0:
                    issues.append({
                        'column': col,
                        'issue': 'Negative values',
                        'count': negative_count
                    })
            
            # Check for extreme outliers (beyond 3 standard deviations)
            mean = self.df[col].mean()
            std = self.df[col].std()
            outliers = ((self.df[col] - mean).abs() > 3 * std).sum()
            if outliers > 0:
                issues.append({
                    'column': col,
                    'issue': 'Outliers (>3 std dev)',
                    'count': outliers
                })
        
        if issues:
            issues_df = pd.DataFrame(issues)
            self.validation_results['value_ranges'] = issues_df
            print(f"\nValue Range Issues:")
            print(issues_df.to_string(index=False))
        else:
            print(f"\nValue Range Check: No issues found")
        
        return issues
    
    def check_date_consistency(self):
        """Check date consistency"""
        issues = []
        
        date_cols = [col for col in self.df.columns if 'date' in col.lower()]
        
        if 'check_in_date' in self.df.columns and 'check_out_date' in self.df.columns:
            # Check if check-out is after check-in
            invalid_dates = (self.df['check_out_date'] <= self.df['check_in_date']).sum()
            if invalid_dates > 0:
                issues.append({
                    'issue': 'Check-out before or same as check-in',
                    'count': invalid_dates
                })
        
        if issues:
            issues_df = pd.DataFrame(issues)
            self.validation_results['date_consistency'] = issues_df
            print(f"\nDate Consistency Issues:")
            print(issues_df.to_string(index=False))
        else:
            print(f"\nDate Consistency Check: No issues found")
        
        return issues
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*50)
        print("DATA VALIDATION REPORT")
        print("="*50)
        
        self.load_data()
        self.check_missing_values()
        self.check_duplicates()
        self.check_data_types()
        self.check_value_ranges()
        self.check_date_consistency()
        
        # Overall assessment
        total_issues = sum([
            len(self.validation_results.get('missing_values', [])),
            self.validation_results.get('duplicates', {}).get('count', 0),
            len(self.validation_results.get('value_ranges', [])),
            len(self.validation_results.get('date_consistency', []))
        ])
        
        print("\n" + "="*50)
        print(f"OVERALL ASSESSMENT")
        print("="*50)
        print(f"Total issues found: {total_issues}")
        
        if total_issues == 0:
            print("✅ Data quality is excellent!")
        elif total_issues < 10:
            print("⚠️  Data quality is good with minor issues")
        else:
            print("❌ Data quality needs improvement")
        
        return self.validation_results


def main():
    """Main validation function"""
    data_file = 'data/processed/hotel_bookings_transformed.csv'
    
    validator = HotelDataValidator(data_file)
    results = validator.generate_validation_report()
    
    return results


if __name__ == "__main__":
    main()
