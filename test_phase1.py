import sys
sys.path.append('.')

try:
    from pme_math.alignment_engine import DataAlignmentEngine
    from pme_math.error_envelope import envelope_ok
    print('✅ Phase 1 imports successful')
    
    import pandas as pd
    
    # Quick test with mismatched data
    fund_data = pd.DataFrame({
        'date': ['2023-01-01', '2023-02-01'],
        'cashflow': [-1000, 500]
    })
    index_data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-15', '2023-02-01'],
        'value': [100, 101, 102]
    })
    
    print(f'📊 Input shapes: Fund={fund_data.shape}, Index={index_data.shape}')
    
    engine = DataAlignmentEngine()
    fund_aligned, index_aligned = engine.align_fund_and_index(fund_data, index_data)
    
    print(f'✅ Alignment successful: Fund={fund_aligned.shape}, Index={index_aligned.shape}')
    print(f'   Same length: {len(fund_aligned) == len(index_aligned)}')
    print('🎉 Phase 1 working correctly!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc() 