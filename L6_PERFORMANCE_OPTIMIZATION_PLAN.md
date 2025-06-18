# L6 PERFORMANCE OPTIMIZATION PLAN

## Performance Bottlenecks Identified

### 🔴 CRITICAL BOTTLENECKS (High Impact)

1. **Pandas iterrows() Usage** - 6 files affected
   - `api_bridge.py`: 4 instances of `iterrows()` 
   - `validation/file_check.py`: 2 instances
   - `schemas.py`: 2 instances
   - `nav_waterfall.py`: 2 instances
   - `reporting/xlsx.py`: 1 instance
   - **Impact**: 10-100x slower than vectorized operations

2. **Inefficient Nested Loops** - Portfolio optimization
   - `portfolio_service.py`: O(n²) correlation matrix calculations
   - **Impact**: Quadratic complexity for large datasets

3. **Temporary File I/O** - PME Engine
   - `pme_engine.py`: Creates temp files for every calculation
   - **Impact**: Disk I/O overhead, file system stress

### 🟡 MODERATE BOTTLENECKS (Medium Impact)

4. **Repeated DataFrame Operations**
   - Multiple date alignment operations
   - Redundant data copying in analysis engine

5. **Inefficient IRR Calculations**
   - Multiple XIRR calls without caching
   - Scipy optimization overhead

### 🟢 MINOR OPTIMIZATIONS (Low Impact)

6. **Loop Optimizations**
   - Range-based loops in reporting
   - List comprehensions that could be vectorized

## Optimization Strategy

### Phase 1: Critical Fixes (Immediate 5-10x speedup)

#### 1.1 Replace iterrows() with vectorized operations
```python
# BEFORE (slow)
for idx, row in df.iterrows():
    result = process_row(row)

# AFTER (fast)
result = df.apply(process_row, axis=1)  # or vectorized operations
```

#### 1.2 Eliminate temporary file I/O
```python
# BEFORE: PME Engine creates temp files
# AFTER: Direct DataFrame operations
```

#### 1.3 Optimize correlation matrix calculation
```python
# BEFORE: Nested loops
# AFTER: Use numpy.corrcoef() or pandas.corr()
```

### Phase 2: Moderate Optimizations (2-3x speedup)

#### 2.1 Implement calculation caching
- Cache IRR calculations
- Cache aligned data operations
- Cache expensive PME metrics

#### 2.2 Optimize date alignment
- Pre-compute common date ranges
- Use pandas merge operations instead of loops

### Phase 3: Minor Optimizations (10-20% speedup)

#### 3.1 Vectorize remaining loops
#### 3.2 Optimize memory usage
#### 3.3 Parallel processing for independent calculations

## Implementation Priority

1. **api_bridge.py** - Replace 4 iterrows() calls ⚡ HIGH IMPACT
2. **pme_engine.py** - Remove temp file I/O ⚡ HIGH IMPACT  
3. **portfolio_service.py** - Vectorize correlation matrix ⚡ HIGH IMPACT
4. **validation/file_check.py** - Replace 2 iterrows() calls 🔶 MEDIUM
5. **schemas.py** - Replace 2 iterrows() calls 🔶 MEDIUM
6. **nav_waterfall.py** - Replace 2 iterrows() calls 🔶 MEDIUM

## Performance Targets

- **Current**: ~366ms for basic PME calculation
- **Target Phase 1**: <50ms (7x improvement)
- **Target Phase 2**: <20ms (18x improvement)  
- **Target Phase 3**: <10ms (36x improvement)

## Measurement Strategy

1. **Before/After Benchmarks**: Profile each optimization
2. **Regression Testing**: Ensure accuracy maintained
3. **Memory Profiling**: Monitor memory usage
4. **Load Testing**: Test with realistic dataset sizes

## Risk Mitigation

- ✅ All optimizations maintain existing API compatibility
- ✅ Comprehensive test coverage ensures correctness
- ✅ Gradual rollout with performance monitoring
- ✅ Fallback mechanisms for edge cases 