# AWS-Apply-TagEditor

- This code its purpose to easy way apply Tags on many resources using csv file extracted from "AWS Resource Explorer > Tag Editor".

---
1ª – Search for the service “AWS Resource Explorer” > “Tag Editor”;

2ª – Select the region as well as the resources and click on "Search resources";

3ª – Wait the result and export .csv file on “Export all tags”;

4ª - Use “convert-csv-xlsx” to convert the file;

---
Apply-Tag v2

- Works with AWS Tag Editor exports;
- Works with AWS Resource Explorer exports;
- Automatically normalizes Tag: xxx → xxx;
- Continues on errors;
- Resumes after interruption;
- Safe DRY_RUN mode;
- Skips already processed ARNs;

Requirements:
    pip install boto3 pandas openpyxl;
