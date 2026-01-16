import great_expectations as gx

# Connection String
CONNECTION_STRING = "mysql+mysqlconnector://admin:admin@mariadb:3306/sirene_dw"

def validate_data():
    context = gx.get_context()

    # 1. Connect to SQL Source
    datasource = context.sources.add_sql(
        name="mariadb_datasource",
        connection_string=CONNECTION_STRING,
    )
    
    # 2. Add Asset (The Table)
    asset = datasource.add_table_asset(
        name="cleaned_sirene",
        table_name="cleaned_stock_etablissement"
    )

    # 3. Define Expectations
    suite = context.add_or_update_expectation_suite("sirene_quality_suite")
    
    batch_request = asset.build_batch_request()
    validator = context.get_validator(batch_request=batch_request, expectation_suite=suite)

    # Rules
    validator.expect_column_values_to_be_unique("siret")
    validator.expect_column_values_to_not_be_null("siren")
    validator.expect_column_value_lengths_to_equal("codePostalEtablissement", 5)

    # 4. Save & Run
    validator.save_expectation_suite()
    
    checkpoint = context.add_or_update_checkpoint(
        name="sirene_checkpoint",
        validator=validator,
    )
    
    results = checkpoint.run()
    
    if not results["success"]:
        print("❌ Data Quality Validation FAILED")
        exit(1)
    else:
        print("✅ Data Quality Validation PASSED")

if __name__ == "__main__":
    validate_data()