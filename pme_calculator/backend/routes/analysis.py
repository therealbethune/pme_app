import logging
from typing import Any

import pandas as pd
from data_processor import IntelligentDataProcessor
from fastapi import APIRouter, HTTPException, Request

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global variables for storing processed data
fund_data = None
index_data = None


@router.post("/process-datasets")
async def process_datasets(request: Request) -> dict[str, Any]:
    """
    Intelligent processing of multiple datasets to create optimal data structure for PME calculations

    Supports:
    - Multiple column naming conventions
    - Automatic data type detection
    - Data validation and cleaning
    - Optimal structure creation
    """
    try:
        form = await request.form()

        datasets = {}
        primary_dataset = None

        # Process uploaded files
        for _key, file in form.items():
            if hasattr(file, "filename") and hasattr(file, "read") and file.filename:
                try:
                    # Read file content
                    content = await file.read()

                    # Determine file type and read accordingly
                    if file.filename.endswith(".csv"):
                        import io

                        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
                    elif file.filename.endswith((".xlsx", ".xls")):
                        import io

                        df = pd.read_excel(io.BytesIO(content))
                    else:
                        continue

                    # Use filename (without extension) as dataset name
                    dataset_name = file.filename.rsplit(".", 1)[0]
                    datasets[dataset_name] = df

                    # If this contains fund-like data, make it primary
                    if any(
                        col.lower()
                        in ["cashflow", "contribution", "distribution", "nav"]
                        for col in df.columns
                    ):
                        primary_dataset = dataset_name

                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {str(e)}")
                    continue

        if not datasets:
            raise HTTPException(status_code=400, detail="No valid datasets provided")

        # Initialize intelligent processor
        processor = IntelligentDataProcessor()

        # Create optimal data structure
        optimal_structure = processor.create_optimal_structure(
            datasets, primary_dataset
        )

        # Store processed data in global state for analysis
        if optimal_structure.calculation_ready:
            global fund_data, index_data
            fund_data = optimal_structure.fund_data
            index_data = optimal_structure.index_data

        # Convert metadata to serializable format
        metadata_dict = {}
        for name, meta in optimal_structure.metadata.items():
            # Safely handle date_range - check if it exists and is subscriptable
            date_range_formatted = None
            try:
                if (
                    hasattr(meta, "date_range")
                    and meta.date_range
                    and isinstance(meta.date_range, list | tuple)
                    and len(meta.date_range) >= 2
                ):
                    date_range_formatted = [
                        meta.date_range[0].isoformat(),
                        meta.date_range[1].isoformat(),
                    ]
                elif hasattr(meta, "date_range") and meta.date_range:
                    # If date_range exists but isn't subscriptable, convert to string
                    date_range_formatted = str(meta.date_range)
            except (AttributeError, TypeError, IndexError) as e:
                logger.warning(f"Could not format date_range for {name}: {e}")
                date_range_formatted = None

            metadata_dict[name] = {
                "name": meta.name,
                "rows": meta.rows,
                "columns": meta.columns,
                "date_range": date_range_formatted,
                "data_quality_score": meta.data_quality_score,
                "missing_data_percentage": meta.missing_data_percentage,
                "column_mappings": [
                    {
                        "original_name": mapping.original_name,
                        "standardized_name": mapping.standardized_name,
                        "data_type": mapping.data_type.value,
                        "confidence": mapping.confidence,
                        "transformations": mapping.transformations,
                    }
                    for mapping in meta.column_mappings
                ],
            }

        return {
            "success": True,
            "calculation_ready": optimal_structure.calculation_ready,
            "metadata": metadata_dict,
            "warnings": optimal_structure.warnings,
            "suggestions": optimal_structure.suggestions,
            "fund_data_preview": (
                optimal_structure.fund_data.head(5).to_dict(orient="records")
                if not optimal_structure.fund_data.empty
                else []
            ),
            "index_data_preview": (
                optimal_structure.index_data.head(5).to_dict(orient="records")
                if optimal_structure.index_data is not None
                else None
            ),
        }

    except Exception as e:
        logger.error(f"Error in intelligent data processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/analyze-columns")
async def analyze_columns(request: Request) -> dict[str, Any]:
    """
    Analyze column types and suggest optimal mappings for a dataset
    """
    try:
        data = await request.json()

        # Extract sample data
        sample_data = data.get("sample_data", {})
        if not sample_data:
            raise HTTPException(status_code=400, detail="No sample data provided")

        # Convert to DataFrame
        df = pd.DataFrame(sample_data)

        # Initialize processor
        processor = IntelligentDataProcessor()

        # Analyze each column
        column_analysis = []
        for col in df.columns:
            sample_values = df[col].dropna().head(10).tolist()
            mapping = processor.detect_column_type(col, sample_values)

            column_analysis.append(
                {
                    "original_name": mapping.original_name,
                    "standardized_name": mapping.standardized_name,
                    "data_type": mapping.data_type.value,
                    "confidence": mapping.confidence,
                    "sample_values": sample_values[:5],  # First 5 sample values
                    "total_values": len(df[col].dropna()),
                    "missing_values": len(df[col]) - len(df[col].dropna()),
                    "suggested_transformations": [],
                }
            )

        return {
            "success": True,
            "total_columns": len(df.columns),
            "total_rows": len(df),
            "column_analysis": column_analysis,
            "recommendations": [
                "Columns with confidence < 0.7 may need manual review",
                "Date columns will be automatically standardized",
                "Currency columns will have symbols and formatting removed",
                "Missing values will be handled appropriately for each data type",
            ],
        }

    except Exception as e:
        logger.error(f"Error in column analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/suggest-structure")
async def suggest_optimal_structure(request: Request) -> dict[str, Any]:
    """
    Suggest optimal data structure for PME calculations based on detected columns
    """
    try:
        data = await request.json()

        detected_types = data.get("detected_types", [])
        if not detected_types:
            raise HTTPException(
                status_code=400, detail="No detected column types provided"
            )

        suggestions = {
            "fund_data_requirements": {
                "essential": ["date", "nav"],
                "cash_flows": {
                    "option1": ["cashflow"],
                    "option2": ["contribution", "distribution"],
                },
                "optional": ["currency", "fund_name", "portfolio_id"],
            },
            "index_data_requirements": {
                "essential": ["date"],
                "values": ["index_value", "price", "level"],
                "optional": ["index_name", "currency"],
            },
            "detected_structure": {},
            "missing_requirements": [],
            "recommendations": [],
        }

        # Analyze detected types
        fund_data_score = 0
        index_data_score = 0

        for col_info in detected_types:
            col_type = col_info.get("data_type")
            confidence = col_info.get("confidence", 0)

            if col_type in ["date", "nav", "cashflow", "contribution", "distribution"]:
                fund_data_score += confidence
            elif col_type in ["date", "index_value", "price"]:
                index_data_score += confidence

        # Determine data structure type
        if fund_data_score > index_data_score:
            suggestions["detected_structure"]["type"] = "fund_data"
            suggestions["detected_structure"]["confidence"] = fund_data_score / len(
                detected_types
            )
        else:
            suggestions["detected_structure"]["type"] = "index_data"
            suggestions["detected_structure"]["confidence"] = index_data_score / len(
                detected_types
            )

        # Check for missing requirements
        detected_type_names = {col["data_type"] for col in detected_types}

        if "date" not in detected_type_names:
            suggestions["missing_requirements"].append(
                "Date column is required for all calculations"
            )

        if suggestions["detected_structure"]["type"] == "fund_data":
            if "nav" not in detected_type_names:
                suggestions["missing_requirements"].append(
                    "NAV (Net Asset Value) column is required"
                )

            has_cashflow = "cashflow" in detected_type_names
            has_contrib_distrib = (
                "contribution" in detected_type_names
                and "distribution" in detected_type_names
            )

            if not (has_cashflow or has_contrib_distrib):
                suggestions["missing_requirements"].append(
                    "Either a cashflow column OR both contribution and distribution columns are required"
                )

        # Generate recommendations
        if not suggestions["missing_requirements"]:
            suggestions["recommendations"].append(
                "✅ All required columns detected - ready for PME calculations"
            )
        else:
            suggestions["recommendations"].append(
                "⚠️ Missing required columns - please review data structure"
            )

        # Column-specific recommendations
        low_confidence_cols = [
            col for col in detected_types if col.get("confidence", 0) < 0.7
        ]
        if low_confidence_cols:
            suggestions["recommendations"].append(
                f"📝 Review {len(low_confidence_cols)} columns with low detection confidence"
            )

        suggestions["recommendations"].append(
            "🔄 Use the 'Process Datasets' endpoint to automatically optimize your data structure"
        )

        return {"success": True, "suggestions": suggestions}

    except Exception as e:
        logger.error(f"Error in structure suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Suggestion failed: {str(e)}")
