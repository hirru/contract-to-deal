import streamlit as st
import requests
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI  # Use OpenAI's GPT model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# Deal API endpoint and key
deal_url = "https://stage-sparkplug-api.enerex.com/api/deal/ConvertPipelineToDealNew"
deal_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik9UUXlRamMzTXpFMFFqbEZRMEl4UmtRNFFUQTRORE5FUWtFMFJFVkdSRFV5TURnNE5rRXpSZyJ9.eyJpc3MiOiJodHRwczovL2VuZXJneWZyYW1ld29ya3MtZGV2LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjExN2FkMmJmNWFkMTAwMTNlZjQzZWEiLCJhdWQiOlsiaHR0cHM6Ly9kZXYuc3BhcmtwbHVnLmVuZXJneS9hcGkvIiwiaHR0cHM6Ly9lbmVyZ3lmcmFtZXdvcmtzLWRldi5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzM3NDUyNjE5LCJleHAiOjE3Mzc1MzkwMTgsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUiLCJhenAiOiJUMGdGVXR2MlZuMTVGWmljSkJ3bGxERDlNU1BtTG9xYSJ9.Q5AX3gQKZIf3ZyN-Xyl7iB3R6FLH6I7rUDjzDHn866X7_UfMRAc5SXZKAKEvHT6PXsPAPavnBt-YXHZk_TIjiRTASe_gFr7YWdMpe-q6HthrnJ9YspcBqSjXi7CU6_0cKHLBYMpzDavf3Qw6FNZy1u6v-xbaWp3cXe9pyAl4DkJcsypKabo0lcFTlAAilcCHan9VhtAwEct3KJam4bJQ0zvFwKLuQPfrXImWzZJ6c9__JL9PK51iXnvQHxOsB9gWRDluMRlYcSlWIRGvz31tmHpG7GujQOODU2fdSXJPaNmFSJwyXT4cxnz6inwVH4mc06gP5BhV6rwNMdyTFmW_Lg"  # Replace with your Deal API key

# Step 1: Load PDF and extract text
def load_pdf_and_extract_text(pdf_path):
    try:
        # Use LangChain's PyPDFLoader to load the PDF
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()  # Load all pages
        text = " ".join(page.page_content for page in pages)  # Combine all pages into a single text
        print(text)
        return text
    except Exception as e:
        st.error(f"Error in load_pdf_and_extract_text: {e}")
        return None

# Step 2: Use GPT to extract fields
def extract_fields_with_gpt(text, open_api_key):
    try:
        # Initialize the GPT model
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Use GPT-4 or GPT-3.5-turbo
            api_key=open_api_key,
            temperature=0.7
        )

        # Define the JSON output parser
        parser = JsonOutputParser(pydantic_object={
            "type": "object",
            "properties": {
                "contact_name": {"type": "string"},
                "billing_address": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zip": {"type": "string"},
                "contact_phone": {"type": "string"},
                "fax": {"type": "string"},
                "email": {"type": "string"},
                "tax_exempt": {"type": "string"},
                "account_number": {"type": "string"},
                "service_address_1": {"type": "string"},
                "service_address_2": {"type": "string"},
                "utility": {"type": "string"},
                "contract_term": {"type": "string"},
                "price": {"type": "string"}
            }
        })

        # Define the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract contract details into JSON with this structure:
                {{
                    "contact_name": "name here",
                    "billing_address": "address here",
                    "city": "city name here",
                    "state": "state name here",
                    "zip": "zip code here",
                    "contact_phone": "phone number here",
                    "fax": "fax number here",
                    "email": "email here",
                    "tax_exempt": "yes or no",
                    "account_number": "account number here",
                    "service_address_1": "address line 1",
                    "service_address_2": "address line 2",
                    "utility": "utility type here",
                    "contract_term": "term here",
                    "price": "price here"
                }}"""),
            ("user", "{input}")
        ])

        # Create the chain
        chain = prompt | llm | parser

        # Pass the entire text to the GPT model
        result = chain.invoke({"input": text})
        return result

    except Exception as e:
        st.error(f"Error in extract_fields_with_gpt: {e}")
        return None

# Step 3: Map extracted data to API schema
def map_fields(extracted_data):
    try:
        fields = {
            "Id": extracted_data.get("Id", 0),
            "DisableWhenRenewing": extracted_data.get("DisableWhenRenewing", True),
            "IsPipeLineToDeal": extracted_data.get("IsPipeLineToDeal", True),
            "Name": extracted_data.get("Name", "2501-NEW-Anirudh Pundir #18"),
            "RenewDealFromName": extracted_data.get("RenewDealFromName", None),
            "RenewDealFromId": extracted_data.get("RenewDealFromId", None),
            "DisplayName": extracted_data.get("DisplayName", None),
            "CompanyId": extracted_data.get("CompanyId", 280),
            "PipelineId": extracted_data.get("PipelineId", 144872),
            "AggregationId": extracted_data.get("AggregationId", None),
            "AggregationTitle": extracted_data.get("AggregationTitle", None),
            "StatusId": extracted_data.get("StatusId", 14),
            "StatusName": extracted_data.get("StatusName", "Unknown"),
            "CustomerId": extracted_data.get("CustomerId", 286242),
            "CustomerName": extracted_data.get("CustomerName", "Anirudh Pundir #18"),
            "SupplierId": extracted_data.get("SupplierId", 92),
            "SupplierName": extracted_data.get("SupplierName", "Supreme Energy Inc."),
            "SalespersonId": extracted_data.get("SalespersonId", 24115),
            "SalespersonName": extracted_data.get("SalespersonName", "abcd abc24234234"),
            "CUSTOMERACCOUNTMANAGERNAME": extracted_data.get("CUSTOMERACCOUNTMANAGERNAME", None),
            "Salespersons": extracted_data.get("Salespersons", []),
            "Products": extracted_data.get("Products", []),
            "BillingTypes": extracted_data.get("BillingTypes", []),
            "ThirdPartyProviderVM": extracted_data.get("ThirdPartyProviderVM", []),
            "ThirdPartyProviderName": extracted_data.get("ThirdPartyProviderName", ""),
            "IsThirdParty": extracted_data.get("IsThirdParty", False),
            "TypeId": extracted_data.get("TypeId", 1),
            "TypeName": extracted_data.get("TypeName", "Electric"),
            "FlavorId": extracted_data.get("FlavorId", 1),
            "FlavorName": extracted_data.get("FlavorName", "Regular"),
            "TaxExempt": extracted_data.get("TaxExempt", 0),
            "Upfront": extracted_data.get("Upfront", False),
            "ContractPeriodInMonth": extracted_data.get("ContractPeriodInMonth", 1),
            "PrimaryAdder": extracted_data.get("PrimaryAdder", 0.007000),
            "Price": extracted_data.get("Price", 0.060000),
            "StateId": extracted_data.get("StateId", 43),
            "StateName": extracted_data.get("state", "Texas"),
            "GreenPercentage": extracted_data.get("GreenPercentage", None),
            "StateDropDown": extracted_data.get("StateDropDown", []),
            "ProductId": extracted_data.get("ProductId", 1),
            "ProductName": extracted_data.get("ProductName", "Fixed"),
            "SupplierProductName": extracted_data.get("SupplierProductName", ""),
            "IsValidContract": extracted_data.get("IsValidContract", 1),
            "IsValidStart": extracted_data.get("IsValidStart", 0),
            "IsValidBookedDate": extracted_data.get("IsValidBookedDate", 1),
            "BookedDate": extracted_data.get("BookedDate", "Jan 21, 2025"),
            "StartDate": extracted_data.get("StartDate", "Jan 22, 2025"),
            "EndDate": extracted_data.get("EndDate", "02/21/2025"),
            "InputEndDate": extracted_data.get("InputEndDate", False),
            "IsActualReadDate": extracted_data.get("IsActualReadDate", False),
            "IsPipelineConverted": extracted_data.get("IsPipelineConverted", True),
            "DealLevel": extracted_data.get("DealLevel", []),
            "DealLevelId": extracted_data.get("DealLevelId", 1981),
            "IsEditable": extracted_data.get("IsEditable", True),
            "IsStateEditable": extracted_data.get("IsStateEditable", False),
            "ParentSystemEndDate": extracted_data.get("ParentSystemEndDate", 0),
            "pcprice": extracted_data.get("pcprice", 0.060000),
            "DealSourceId": extracted_data.get("DealSourceId", 12),
            "DealSourceDropDown": extracted_data.get("DealSourceDropDown", []),
            "DealReferredById": extracted_data.get("DealReferredById", 19),
            "DealReferredByName": extracted_data.get("DealReferredByName", "Samson"),
            "DealReferredByNameLable": extracted_data.get("DealReferredByNameLable", "Customer Name"),
            "DealSourceName": extracted_data.get("DealSourceName", "Customer Referral"),
            "ResidualPaymentTypeList": extracted_data.get("ResidualPaymentTypeList", []),
            "ResidualPaymentType": extracted_data.get("ResidualPaymentType", 1),
            "CustomFlagsRenew": extracted_data.get("CustomFlagsRenew", []),
            "SelectedFlags": extracted_data.get("SelectedFlags", None),
            "UOMDropdownMaster": extracted_data.get("UOMDropdownMaster", []),
            "UOMDropdown": extracted_data.get("UOMDropdown", []),
            "Unit": extracted_data.get("Unit", "kWh"),
            "ConversionFactor": extracted_data.get("ConversionFactor", 1),
            "QuoteTypes": extracted_data.get("QuoteTypes", []),
            "UpfrontSchedule": extracted_data.get("UpfrontSchedule", []),
            "Custom_1": extracted_data.get("Custom_1", ""),
            "Custom_2": extracted_data.get("Custom_2", ""),
            "Custom_3": extracted_data.get("Custom_3", ""),
            "GetRenewed": extracted_data.get("GetRenewed", 3),
            "Custom_4": extracted_data.get("Custom_4", ""),
            "Custom_5": extracted_data.get("Custom_5", ""),
            "QuoteSentType": extracted_data.get("QuoteSentType", 3),
            "Custom_1_Lable": extracted_data.get("Custom_1_Lable", ""),
            "Custom_2_Lable": extracted_data.get("Custom_2_Lable", ""),
            "Custom_3_Lable": extracted_data.get("Custom_3_Lable", ""),
            "Custom_4_Lable": extracted_data.get("Custom_4_Lable", ""),
            "Custom_5_Lable": extracted_data.get("Custom_5_Lable", ""),
            "UsageEndDate": extracted_data.get("UsageEndDate", ""),
            "CustomFieldData": extracted_data.get("CustomFieldData", []),
            "NonCustomerReferralDropDown": extracted_data.get("NonCustomerReferralDropDown", []),
            "TaxExemptOptions": extracted_data.get("TaxExemptOptions", []),
            "PipelineAccTrandlst": extracted_data.get("PipelineAccTrandlst", []),
            "CostComponents": extracted_data.get("CostComponents", []),
            "CostComponentIds": extracted_data.get("CostComponentIds", ""),
            "CustomerContacts": extracted_data.get("CustomerContacts", []),
            "SupplierContacts": extracted_data.get("SupplierContacts", []),
            "BandWidth": extracted_data.get("BandWidth", ""),
            "ConvertedDealId": extracted_data.get("ConvertedDealId", 0),
            "ValidatedPipelineAccounts": extracted_data.get("ValidatedPipelineAccounts", []),
            "PipelineAccTrandlstOld": extracted_data.get("PipelineAccTrandlstOld", []),
            "errors": extracted_data.get("errors", []),
            "DealLevelName": extracted_data.get("DealLevelName", "Large C&I"),
            "SearchTerm": extracted_data.get("SearchTerm", ""),
            "DealTypeId": extracted_data.get("DealTypeId", 1),
            "DealTypeName": extracted_data.get("DealTypeName", "Electric"),
            "ExpectedUsage": extracted_data.get("ExpectedUsage", 0),
            "ExpectedClosureDate": extracted_data.get("ExpectedClosureDate", None),
            "ExpectedStartDate": extracted_data.get("ExpectedStartDate", None),
            "ContractEndDate": extracted_data.get("ContractEndDate", None),
            "DealStatusId": extracted_data.get("DealStatusId", 3),
            "LastActicityId": extracted_data.get("LastActicityId", 16925),
            "CurrentProductId": extracted_data.get("CurrentProductId", None),
            "CurrentProductName": extracted_data.get("CurrentProductName", ""),
            "ExpectedUnitMargin": extracted_data.get("ExpectedUnitMargin", None),
            "ExpectedClosePercentage": extracted_data.get("ExpectedClosePercentage", None),
            "CurrentPrice": extracted_data.get("CurrentPrice", None),
            "CurrentSupplier": extracted_data.get("CurrentSupplier", None),
            "CurrentTerm": extracted_data.get("CurrentTerm", None),
            "LostReason": extracted_data.get("LostReason", None),
            "FiscalYear": extracted_data.get("FiscalYear", None),
            "FiscalQuarter": extracted_data.get("FiscalQuarter", 2025),
            "ExternalId": extracted_data.get("ExternalId", None),
            "CustomFlagId": extracted_data.get("CustomFlagId", None),
            "Customer": extracted_data.get("Customer", None),
            "Salesperson": extracted_data.get("Salesperson", None),
            "DealType": extracted_data.get("DealType", None),
            "DealStatus": extracted_data.get("DealStatus", {}),
            "State": extracted_data.get("State", None),
            "DealSource": extracted_data.get("DealSource", None),
            "ReferenceKey": extracted_data.get("ReferenceKey", "SPQA-OP-00004852"),
            "PipelineQuoteSent": extracted_data.get("PipelineQuoteSent", None),
            "QuotationSentLineItem": extracted_data.get("QuotationSentLineItem", None),
            "PipelineStageActivities": extracted_data.get("PipelineStageActivities", None),
            "LeadId": extracted_data.get("LeadId", None),
            "LeadName": extracted_data.get("LeadName", None),
            "RenewDealId": extracted_data.get("RenewDealId", None),
            "RenewDealName": extracted_data.get("RenewDealName", ""),
            "IsHUVarianceAvailable": extracted_data.get("IsHUVarianceAvailable", False),
            "ConsultingTypeId": extracted_data.get("ConsultingTypeId", None),
            "ConsultingTypeName": extracted_data.get("ConsultingTypeName", None),
            "IsConfirmedForMultipleUtilityForMatrix": extracted_data.get("IsConfirmedForMultipleUtilityForMatrix", None),
            "ConfirmedByForMultipleUtilityForMatrix": extracted_data.get("ConfirmedByForMultipleUtilityForMatrix", None),
            "ConfirmedOnForMultipleUtilityForMatrix": extracted_data.get("ConfirmedOnForMultipleUtilityForMatrix", None),
            "IsConfirmedForMultipleUtilityForContract": extracted_data.get("IsConfirmedForMultipleUtilityForContract", None),
            "ConfirmedByForMultipleUtilityForContract": extracted_data.get("ConfirmedByForMultipleUtilityForContract", None),
            "ConfirmedOnForMultipleUtilityForContract": extracted_data.get("ConfirmedOnForMultipleUtilityForContract", None),
            "Type": extracted_data.get("Type", 1),
            "EstimatedRevenue": extracted_data.get("EstimatedRevenue", 0),
            "RetainViewRight": extracted_data.get("RetainViewRight", None),
            "IsPowerPortal": extracted_data.get("IsPowerPortal", None),
            "IsSendToSupplierEnrollList": extracted_data.get("IsSendToSupplierEnrollList", None),
            "IsEnrollWithCCA": extracted_data.get("IsEnrollWithCCA", None),
            "AggregationPipelineMap": extracted_data.get("AggregationPipelineMap", None),
            "PipelineAccount": extracted_data.get("PipelineAccount", None),
            "IncludeDroppedAccount": extracted_data.get("IncludeDroppedAccount", None),
            "OptOutDate": extracted_data.get("OptOutDate", None),
            "IsActionEnable": extracted_data.get("IsActionEnable", None),
            "CustomFlags": extracted_data.get("CustomFlags", None),
            "DataRights": extracted_data.get("DataRights", None),
            "PipelineContacts": extracted_data.get("PipelineContacts", []),
            "PipelineAddress": extracted_data.get("PipelineAddress", []),
            "LastActivityName": extracted_data.get("LastActivityName", None),
            "TotalPkKw": extracted_data.get("TotalPkKw", 0),
            "TotalPkKwLf": extracted_data.get("TotalPkKwLf", 0),
            "TotalCapacityValue": extracted_data.get("TotalCapacityValue", 0),
            "TotalCapacityLfValue": extracted_data.get("TotalCapacityLfValue", 0),
            "TotalNsplValue": extracted_data.get("TotalNsplValue", 0),
            "TotalNsplLfValue": extracted_data.get("TotalNsplLfValue", 0),
            "TotalFuturePCL": extracted_data.get("TotalFuturePCL", 0),
            "TotalFutureNSPL": extracted_data.get("TotalFutureNSPL", 0),
            "TotalFuturePclLF": extracted_data.get("TotalFuturePclLF", True),
            "TotalFutureNsplLF": extracted_data.get("TotalFutureNsplLF", True),
            "ParentCustomerID": extracted_data.get("ParentCustomerID", None),
            "ParentCustomer": extracted_data.get("ParentCustomer", None),
            "NoteCount": extracted_data.get("NoteCount", None),
            "DisplayUnitMargin": extracted_data.get("DisplayUnitMargin", None),
            "DisplayCurrentPrice": extracted_data.get("DisplayCurrentPrice", None),
            "SyncValuesWithExternalSystems": extracted_data.get("SyncValuesWithExternalSystems", {}),
            "SyncEntityType": extracted_data.get("SyncEntityType", 8),
            "SyncEnabled": extracted_data.get("SyncEnabled", True),
            "SyncId": extracted_data.get("SyncId", 144872),
            "SyncActionUserId": extracted_data.get("SyncActionUserId", True),
            "SyncSecondId": extracted_data.get("SyncSecondId", None),
            "SyncCompanyId": extracted_data.get("SyncCompanyId", 0),
            "SyncFieldsToCompare": extracted_data.get("SyncFieldsToCompare", []),
            "ExternalLinks": extracted_data.get("ExternalLinks", []),
            "ExpectedUnitMarginDisplay": extracted_data.get("ExpectedUnitMarginDisplay", None),
            "ExpectedUsageDisplay": extracted_data.get("ExpectedUsageDisplay", None),
            "CurrentPriceDisplay": extracted_data.get("CurrentPriceDisplay", None),
            "VendorId": extracted_data.get("VendorId", 0),
            "VendorName": extracted_data.get("VendorName", None),
            "SolarBuildingTypeId": extracted_data.get("SolarBuildingTypeId", 0),
            "IsClientPOC": extracted_data.get("IsClientPOC", None),
            "IsClientBuilding": extracted_data.get("IsClientBuilding", None),
            "SolarReasonId": extracted_data.get("SolarReasonId", None),
            "SolarMountTypeId": extracted_data.get("SolarMountTypeId", None),
            "RoofAgeYear": extracted_data.get("RoofAgeYear", None),
            "RoofMeterial": extracted_data.get("RoofMeterial", None),
            "SolarGroundMountId": extracted_data.get("SolarGroundMountId", None),
            "SolarDesignId": extracted_data.get("SolarDesignId", None),
            "SolarFinancingId": extracted_data.get("SolarFinancingId", None),
            "EnergyMeasuresId": extracted_data.get("EnergyMeasuresId", None),
            "SupplyContractId": extracted_data.get("SupplyContractId", None),
            "MountWarranty": extracted_data.get("MountWarranty", None),
            "Comment": extracted_data.get("Comment", None),
            "IsUtilityBillProvided": extracted_data.get("IsUtilityBillProvided", None),
            "IsSolarProject": extracted_data.get("IsSolarProject", None),
            "IsSentToVendor": extracted_data.get("IsSentToVendor", None),
            "IsExchangeConnected": extracted_data.get("IsExchangeConnected", None),
            "VendorLogo": extracted_data.get("VendorLogo", None),
            "Active": extracted_data.get("Active", True),
            "CustomerContactSigneeId": extracted_data.get("CustomerContactSigneeId", None),
            "SupplierContactSigneeId": extracted_data.get("SupplierContactSigneeId", None),
        }

        return fields
    except Exception as e:
        st.error(f"Error in map_fields: {e}")
        return None

# Step 4: Send mapped data to the Deal API
def send_to_api(mapped_fields):
    try:
        headers = {
            "accept": "*/*",
            "authorization": f"Bearer {deal_token}",
            "content-type": "application/json",
        }
        response = requests.post(deal_url, headers=headers, json=mapped_fields)
        return response.json()
    except Exception as e:
        st.error(f"Error in send_to_api: {e}")
        return None

# Streamlit App
def main():
    st.title("AI-Powered Contract Processing POC")
    st.write("Upload a PDF contract to extract and map data to the Deal API.")

    # File upload
    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    uploaded_file = st.file_uploader("Upload a PDF contract", type="pdf")
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        temp_file_path = os.path.join(os.getcwd(), "temp.pdf")
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Step 1: Load PDF and extract text
        st.write("Loading PDF and extracting text...")
        text = load_pdf_and_extract_text(temp_file_path)
        if text:
            st.success("Text extraction successful!")

            # Step 2: Extract fields using GPT
            st.write("Extracting fields using GPT...")
            extracted_data = extract_fields_with_gpt(text, openai_api_key)
            if extracted_data:
                st.success("Field extraction successful!")
                st.write("**Extracted Data:**")
                st.json(extracted_data)  # Show extracted data in JSON format

                # Step 3: Map fields to API schema
                st.write("Mapping fields to API schema...")
                mapped_fields = map_fields(extracted_data)
                if mapped_fields:
                    st.success("Field mapping successful!")
                    st.write("**Mapped Fields:**")
                    st.json(mapped_fields)

                    # Step 4: Send to API
                    st.write("Sending data to API...")
                    api_response = send_to_api(mapped_fields)
                    if api_response:
                        st.success("API call successful!")
                        # st.write("**API Response:**")
                        # st.json(api_response)
                    else:
                        st.error("Failed to send data to API.")
                else:
                    st.error("Failed to map fields.")
            else:
                st.error("Failed to extract fields.")
        else:
            st.error("Failed to extract text from PDF.")

        # Clean up temporary file
        os.remove(temp_file_path)

# Run the Streamlit app
if __name__ == "__main__":
    main()