# Databricks notebook source
import csv
import hashlib
import json
import random
import re
import shutil
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path


SEED = 20261117
START_YEAR = 2025
START_MONTH = 11
PERIOD_COUNT = 12
READY_PERIOD_COUNT = 10
PHARMACY_COUNT = 500
MEDICAL_ROWS_PER_PERIOD = 4_500
PHARMACY_ROWS_PER_PERIOD = 5_500
SALES_ROWS_PER_PERIOD = 12_500
WHOLESALER_ROWS_PER_YEAR = 250_000

PRODUCTS = (
    {"product_code": "99999-0101-01", "material_code": "CGM-SENSOR-01", "unit_rebate": Decimal("85.00")},
    {"product_code": "99999-0102-01", "material_code": "CGM-SENSOR-02", "unit_rebate": Decimal("105.00")},
    {"product_code": "99999-0201-01", "material_code": "CGM-READER-01", "unit_rebate": Decimal("140.00")},
    {"product_code": "99999-0301-01", "material_code": "CGM-TRANSMIT-01", "unit_rebate": Decimal("120.00")},
)

NAME_PREFIXES = (
    "Aster", "Cedar", "Harbor", "Juniper", "Lumen", "Meadow", "Orchard", "Pioneer",
    "Quartz", "Summit", "Timber", "Willow", "Zephyr", "Briar", "Cobalt", "Elm",
)
NAME_SUFFIXES = ("Care Pharmacy", "Community Pharmacy", "Health Pharmacy", "Family Pharmacy")
STREET_NAMES = ("Aster Loop", "Beacon Avenue", "Cedar Way", "Juniper Road", "Meadow Lane", "Summit Street")
STATE_CODES = ("AZ", "CA", "CO", "FL", "GA", "IL", "MA", "NC", "NY", "OH", "OR", "PA", "TX", "UT", "VA", "WA")

MEDICAL_FIELDS = (
    "medClaimId", "billingEntityName", "billingNpi", "serviceFromDate", "productCode",
    "unitsBilled", "rebateUnitsRequested", "rebateAmount", "entityAddress", "entityPhone",
    "entityFax", "receivedTimestamp",
)
PHARMACY_FIELDS = (
    "RX_CLAIM_NBR", "PHARMACY_NAME", "NCPDP_ID", "FILL_DATE", "PRODUCT_NDC",
    "QTY_DISPENSED", "REBATE_UNITS", "REBATE_AMT", "STORE_ADDR", "PHONE_NBR",
    "FAX_NBR", "SUBMISSION_TS",
)
SALES_FIELDS = (
    "SALES_DOC_NBR", "SOLD_TO_ACCT", "SHIP_TO_NAME", "SHIP_TO_ADDR", "MATERIAL_CD",
    "QTY_SHIPPED", "NET_AMT", "SHIP_DT", "DOC_TYPE",
)
WHOLESALER_FIELDS = (
    "Transaction_ID", "Wholesaler_Customer_ID", "Customer_Name", "Customer_Address",
    "Customer_Phone", "Customer_Fax", "NDC", "Transaction_Type", "Quantity", "Invoice_Date",
)


def widget_value(name: str, default: str) -> str:
    try:
        dbutils.widgets.text(name, default)
        return dbutils.widgets.get(name)
    except NameError:
        return default


def validate_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def add_months(year: int, month: int, offset: int) -> tuple[int, int]:
    absolute = year * 12 + month - 1 + offset
    return absolute // 12, absolute % 12 + 1


def stable_random(*parts: object) -> random.Random:
    material = "|".join(str(part) for part in (SEED, *parts))
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def allocate_cents(total_dollars: int, count: int) -> list[Decimal]:
    total_cents = total_dollars * 100
    quotient, remainder = divmod(total_cents, count)
    return [Decimal(quotient + (1 if index < remainder else 0)) / 100 for index in range(count)]


EXCESS_EXPOSURES = allocate_cents(5_600_000, 84)
CROSS_CHANNEL_EXPOSURES = allocate_cents(2_400_000, 48)
COMBINED_EXPOSURES = allocate_cents(2_000_000, 24)


def pharmacy(index: int) -> dict[str, str]:
    prefix = NAME_PREFIXES[index % len(NAME_PREFIXES)]
    suffix = NAME_SUFFIXES[(index // len(NAME_PREFIXES)) % len(NAME_SUFFIXES)]
    state = STATE_CODES[index % len(STATE_CODES)]
    city_number = index % 73 + 1
    street_number = 100 + index * 7
    street = STREET_NAMES[index % len(STREET_NAMES)]
    phone_serial = index % 100
    area_code = 201 + (index % 70)
    return {
        "canonical_id": f"PHM-{index + 1:04d}",
        "legal_name": f"{prefix} {index + 1:04d} {suffix}",
        "dba_name": f"{prefix} {index + 1:04d} Rx",
        "address": f"{street_number} {street}, Demo City {city_number:02d}, {state} {80000 + index:05d}",
        "phone": f"{area_code}-555-{100 + phone_serial:04d}",
        "fax": f"{area_code}-555-{200 + phone_serial:04d}",
        "npi": f"8{index + 1:09d}",
        "ncpdp": f"7{index + 1:06d}",
        "sales_account": f"S{index + 1:07d}",
        "wholesaler_account": f"W{index + 1:07d}",
        "state": state,
    }


PHARMACIES = tuple(pharmacy(index) for index in range(PHARMACY_COUNT))
COMBINED_ALIAS_INDICES = {(23 * index + 211) % PHARMACY_COUNT for index in range(24)}
FRAUD_PHARMACY_INDICES = (
    {(17 * index + 11) % PHARMACY_COUNT for index in range(84)}
    | {(19 * index + 101) % PHARMACY_COUNT for index in range(48)}
    | COMBINED_ALIAS_INDICES
)
BENIGN_ALIAS_INDICES: set[int] = set()
alias_candidate = 0
while len(BENIGN_ALIAS_INDICES) < 36:
    candidate = (29 * alias_candidate + 37) % PHARMACY_COUNT
    if candidate not in FRAUD_PHARMACY_INDICES:
        BENIGN_ALIAS_INDICES.add(candidate)
    alias_candidate += 1
ALIAS_INDICES = COMBINED_ALIAS_INDICES | BENIGN_ALIAS_INDICES


def alias_name(pharmacy_record: dict[str, str], style: str) -> str:
    pharmacy_index = int(pharmacy_record["canonical_id"].split("-")[1]) - 1
    if pharmacy_index not in ALIAS_INDICES:
        return pharmacy_record["legal_name"]
    if style == "medical":
        return pharmacy_record["legal_name"].replace(" Pharmacy", " PHCY")
    if style == "combined":
        return pharmacy_record["dba_name"].replace(" ", "-")
    return pharmacy_record["dba_name"]


def normalized_contact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def service_day(year: int, month: int, ordinal: int) -> date:
    return date(year, month, ordinal % monthrange(year, month)[1] + 1)


def medical_record(
    claim_id: str,
    pharmacy_record: dict[str, str],
    product: dict[str, object],
    service_date: str,
    units: int,
    rebate_amount: Decimal,
    received_at: str,
    name_style: str = "medical",
) -> dict[str, object]:
    return {
        "medClaimId": claim_id,
        "billingEntityName": alias_name(pharmacy_record, name_style),
        "billingNpi": pharmacy_record["npi"],
        "serviceFromDate": service_date,
        "productCode": product["product_code"],
        "unitsBilled": units,
        "rebateUnitsRequested": units,
        "rebateAmount": f"{rebate_amount:.2f}",
        "entityAddress": pharmacy_record["address"],
        "entityPhone": pharmacy_record["phone"],
        "entityFax": pharmacy_record["fax"],
        "receivedTimestamp": received_at,
    }


def pharmacy_record(
    claim_id: str,
    pharmacy_data: dict[str, str],
    product: dict[str, object],
    fill_date: str,
    units: int,
    rebate_amount: Decimal,
    submitted_at: str,
    name_style: str = "pharmacy",
) -> dict[str, object]:
    return {
        "RX_CLAIM_NBR": claim_id,
        "PHARMACY_NAME": alias_name(pharmacy_data, name_style),
        "NCPDP_ID": pharmacy_data["ncpdp"],
        "FILL_DATE": fill_date,
        "PRODUCT_NDC": product["product_code"],
        "QTY_DISPENSED": units,
        "REBATE_UNITS": units,
        "REBATE_AMT": f"{rebate_amount:.2f}",
        "STORE_ADDR": pharmacy_data["address"],
        "PHONE_NBR": pharmacy_data["phone"],
        "FAX_NBR": pharmacy_data["fax"],
        "SUBMISSION_TS": submitted_at,
    }


def build_claims(period_index: int, year: int, month: int) -> tuple[list[dict], list[dict], list[dict]]:
    period = f"{year}{month:02d}"
    medical: list[dict] = []
    pharmacy_claims: list[dict] = []
    special_movements: list[dict] = []
    excluded_pairs: set[tuple[str, str]] = set()

    for local_index in range(7):
        case_index = period_index * 7 + local_index
        pharmacy_data = PHARMACIES[(17 * case_index + 11) % PHARMACY_COUNT]
        product = PRODUCTS[case_index % len(PRODUCTS)]
        units = 240 + local_index * 5
        supported_units = 40 + local_index
        event_date = service_day(year, month, 4 + local_index)
        claim_id = f"RX{period}{len(pharmacy_claims) + 1:06d}"
        pharmacy_claims.append(
            pharmacy_record(
                claim_id,
                pharmacy_data,
                product,
                event_date.isoformat(),
                units,
                EXCESS_EXPOSURES[case_index],
                f"{event_date.isoformat()}T18:15:00Z",
            )
        )
        excluded_pairs.add((pharmacy_data["canonical_id"], str(product["product_code"])))
        special_movements.append(
            {"pharmacy": pharmacy_data, "product": product, "quantity": supported_units, "date": event_date}
        )

    for local_index in range(4):
        case_index = period_index * 4 + local_index
        pharmacy_data = PHARMACIES[(19 * case_index + 101) % PHARMACY_COUNT]
        product = PRODUCTS[(case_index + 1) % len(PRODUCTS)]
        units = 18 + local_index
        event_date = service_day(year, month, 12 + local_index)
        amount = CROSS_CHANNEL_EXPOSURES[case_index]
        medical.append(
            medical_record(
                f"MC{period}{len(medical) + 1:06d}", pharmacy_data, product, event_date.isoformat(), units,
                amount, f"{event_date.isoformat()}T16:20:00Z",
            )
        )
        pharmacy_claims.append(
            pharmacy_record(
                f"RX{period}{len(pharmacy_claims) + 1:06d}", pharmacy_data, product, event_date.isoformat(), units,
                amount, f"{event_date.isoformat()}T17:05:00Z",
            )
        )
        excluded_pairs.add((pharmacy_data["canonical_id"], str(product["product_code"])))
        special_movements.append({"pharmacy": pharmacy_data, "product": product, "quantity": units, "date": event_date})

    for local_index in range(2):
        case_index = period_index * 2 + local_index
        pharmacy_data = PHARMACIES[(23 * case_index + 211) % PHARMACY_COUNT]
        product = PRODUCTS[(case_index + 2) % len(PRODUCTS)]
        units = 260 + local_index * 10
        event_date = service_day(year, month, 20 + local_index)
        amount = COMBINED_EXPOSURES[case_index]
        medical.append(
            medical_record(
                f"MC{period}{len(medical) + 1:06d}", pharmacy_data, product, event_date.isoformat(), units,
                amount, f"{event_date.isoformat()}T14:25:00Z", "combined",
            )
        )
        pharmacy_claims.append(
            pharmacy_record(
                f"RX{period}{len(pharmacy_claims) + 1:06d}", pharmacy_data, product, event_date.isoformat(), units,
                amount, f"{event_date.isoformat()}T15:10:00Z", "combined",
            )
        )
        excluded_pairs.add((pharmacy_data["canonical_id"], str(product["product_code"])))
        special_movements.append({"pharmacy": pharmacy_data, "product": product, "quantity": 45, "date": event_date})

    medical_rng = stable_random("medical", period)
    while len(medical) < MEDICAL_ROWS_PER_PERIOD - 5:
        row_number = len(medical) + 1
        pharmacy_data = PHARMACIES[medical_rng.randrange(PHARMACY_COUNT)]
        product = PRODUCTS[medical_rng.randrange(len(PRODUCTS))]
        if (pharmacy_data["canonical_id"], str(product["product_code"])) in excluded_pairs:
            continue
        event_date = service_day(year, month, row_number)
        units = medical_rng.randint(1, 5)
        amount = Decimal(units) * product["unit_rebate"]
        medical.append(
            medical_record(
                f"MC{period}{row_number:06d}", pharmacy_data, product, event_date.isoformat(), units, amount,
                f"{event_date.isoformat()}T{12 + row_number % 8:02d}:{row_number % 60:02d}:00Z",
            )
        )

    pharmacy_rng = stable_random("pharmacy", period)
    while len(pharmacy_claims) < PHARMACY_ROWS_PER_PERIOD - 5:
        row_number = len(pharmacy_claims) + 1
        pharmacy_data = PHARMACIES[pharmacy_rng.randrange(PHARMACY_COUNT)]
        product = PRODUCTS[pharmacy_rng.randrange(len(PRODUCTS))]
        if (pharmacy_data["canonical_id"], str(product["product_code"])) in excluded_pairs:
            continue
        event_date = service_day(year, month, row_number)
        units = pharmacy_rng.randint(1, 5)
        amount = Decimal(units) * product["unit_rebate"]
        pharmacy_claims.append(
            pharmacy_record(
                f"RX{period}{row_number:06d}", pharmacy_data, product, event_date.isoformat(), units, amount,
                f"{event_date.isoformat()}T{11 + row_number % 9:02d}:{row_number % 60:02d}:00Z",
            )
        )

    medical_regular_start = 6
    pharmacy_regular_start = 13
    for offset in range(25):
        medical[medical_regular_start + offset]["billingEntityName"] += " "
        pharmacy_claims[pharmacy_regular_start + offset]["PHARMACY_NAME"] += " "
    for offset in range(12):
        medical[medical_regular_start + 30 + offset]["entityFax"] = ""
    for offset in range(13):
        pharmacy_claims[pharmacy_regular_start + 30 + offset]["PHONE_NBR"] = ""
    medical[medical_regular_start + 50]["productCode"] = "BAD-CODE-M"
    pharmacy_claims[pharmacy_regular_start + 50]["PRODUCT_NDC"] = "BAD-CODE-P"

    prior_year, prior_month = add_months(year, month, -1)
    for offset in range(10):
        late_date = service_day(prior_year, prior_month, offset + 2)
        medical[medical_regular_start + 60 + offset]["serviceFromDate"] = late_date.isoformat()
        pharmacy_claims[pharmacy_regular_start + 60 + offset]["FILL_DATE"] = late_date.isoformat()

    for offset in range(2):
        medical[medical_regular_start + 80 + offset]["medClaimId"] = ""
    pharmacy_claims[pharmacy_regular_start + 80]["RX_CLAIM_NBR"] = ""
    medical[medical_regular_start + 90]["rebateUnitsRequested"] = -1
    pharmacy_claims[pharmacy_regular_start + 90]["REBATE_UNITS"] = 0
    medical[medical_regular_start + 100]["serviceFromDate"] = f"{year}-99-99"
    pharmacy_claims[pharmacy_regular_start + 100]["FILL_DATE"] = f"{year}-99-99"

    medical.extend(dict(record) for record in medical[-10:-5])
    pharmacy_claims.extend(dict(record) for record in pharmacy_claims[-10:-5])
    return medical, pharmacy_claims, special_movements


def build_reference(year: int, month: int, period_index: int) -> list[dict]:
    records = []
    for index, pharmacy_data in enumerate(PHARMACIES):
        if 20 <= index < 40:
            opened_offset = ((index - 20) * PERIOD_COUNT) // 20
            opened_year, opened_month = add_months(START_YEAR, START_MONTH, opened_offset)
            status = "ACTIVE" if period_index >= opened_offset else "PENDING"
        else:
            opened_year, opened_month = 2020, 1
            status = "ACTIVE"
        closed_date = None
        if index < 20 and period_index >= 8 + index % 4:
            close_year, close_month = add_months(START_YEAR, START_MONTH, 8 + index % 4)
            closed_date = date(close_year, close_month, monthrange(close_year, close_month)[1]).isoformat()
            status = "CLOSED"
        records.append(
            {
                "sourceEntityId": f"REF-{index + 1:06d}",
                "legalName": pharmacy_data["legal_name"],
                "doingBusinessAs": alias_name(pharmacy_data, "pharmacy"),
                "address": pharmacy_data["address"],
                "phone": pharmacy_data["phone"],
                "fax": pharmacy_data["fax"],
                "status": status,
                "effectiveDate": date(opened_year, opened_month, 1).isoformat(),
                "closedDate": closed_date,
            }
        )
    return records


def build_movements(
    period_index: int,
    year: int,
    month: int,
    special_movements: list[dict],
) -> tuple[list[dict], list[dict]]:
    period = f"{year}{month:02d}"
    sales: list[dict] = []
    wholesaler: list[dict] = []
    excluded_pairs = {
        (movement["pharmacy"]["canonical_id"], str(movement["product"]["product_code"]))
        for movement in special_movements
    }

    for movement_index, movement in enumerate(special_movements):
        pharmacy_data = movement["pharmacy"]
        product = movement["product"]
        quantity = movement["quantity"]
        event_date = movement["date"]
        sales.append(
            {
                "SALES_DOC_NBR": f"SD{period}{movement_index + 1:07d}",
                "SOLD_TO_ACCT": pharmacy_data["sales_account"],
                "SHIP_TO_NAME": pharmacy_data["legal_name"],
                "SHIP_TO_ADDR": pharmacy_data["address"],
                "MATERIAL_CD": product["material_code"],
                "QTY_SHIPPED": quantity,
                "NET_AMT": f"{Decimal(quantity) * Decimal('190.00'):.2f}",
                "SHIP_DT": event_date.isoformat(),
                "DOC_TYPE": "SHIPMENT",
            }
        )

    sales_rng = stable_random("sales", period)
    while len(sales) < SALES_ROWS_PER_PERIOD:
        row_number = len(sales) + 1
        pharmacy_data = PHARMACIES[sales_rng.randrange(PHARMACY_COUNT)]
        product = PRODUCTS[sales_rng.randrange(len(PRODUCTS))]
        if (pharmacy_data["canonical_id"], str(product["product_code"])) in excluded_pairs:
            continue
        quantity = sales_rng.randint(6, 36)
        is_return = row_number % 23 == 0
        signed_quantity = -quantity if is_return else quantity
        event_date = service_day(year, month, row_number)
        sales.append(
            {
                "SALES_DOC_NBR": f"SD{period}{row_number:07d}",
                "SOLD_TO_ACCT": pharmacy_data["sales_account"],
                "SHIP_TO_NAME": pharmacy_data["legal_name"],
                "SHIP_TO_ADDR": pharmacy_data["address"],
                "MATERIAL_CD": product["material_code"],
                "QTY_SHIPPED": signed_quantity,
                "NET_AMT": f"{Decimal(signed_quantity) * Decimal('190.00'):.2f}",
                "SHIP_DT": event_date.isoformat(),
                "DOC_TYPE": "RETURN" if is_return else "SHIPMENT",
            }
        )

    wholesaler_target = WHOLESALER_ROWS_PER_YEAR // PERIOD_COUNT + (1 if period_index < WHOLESALER_ROWS_PER_YEAR % PERIOD_COUNT else 0)
    wholesaler_rng = stable_random("wholesaler", period)
    while len(wholesaler) < wholesaler_target:
        row_number = len(wholesaler) + 1
        pharmacy_data = PHARMACIES[wholesaler_rng.randrange(PHARMACY_COUNT)]
        product = PRODUCTS[wholesaler_rng.randrange(len(PRODUCTS))]
        if (pharmacy_data["canonical_id"], str(product["product_code"])) in excluded_pairs:
            continue
        quantity = wholesaler_rng.randint(4, 30)
        transaction_type = "RETURN" if row_number % 31 == 0 else "SALE"
        event_date = service_day(year, month, row_number + 5)
        wholesaler.append(
            {
                "Transaction_ID": f"WT{period}{row_number:07d}",
                "Wholesaler_Customer_ID": pharmacy_data["wholesaler_account"],
                "Customer_Name": alias_name(pharmacy_data, "pharmacy"),
                "Customer_Address": pharmacy_data["address"],
                "Customer_Phone": pharmacy_data["phone"],
                "Customer_Fax": pharmacy_data["fax"],
                "NDC": product["product_code"],
                "Transaction_Type": transaction_type,
                "Quantity": quantity,
                "Invoice_Date": event_date.strftime("%m/%d/%Y"),
            }
        )
    return sales, wholesaler


def write_csv_file(path: Path, rows: list[dict], fields: tuple[str, ...], delimiter: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=delimiter, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl_file(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def file_metadata(path: Path, row_count: int, quantity_total: int | None, amount_total: Decimal | None) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "fileName": path.name,
        "relativePath": str(path.parent.name + "/" + path.name),
        "recordCount": row_count,
        "quantityTotal": quantity_total,
        "amountTotal": f"{amount_total:.2f}" if amount_total is not None else None,
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def generate_period(root: Path, period_index: int, year: int, month: int) -> dict:
    period_label = f"{year}-{month:02d}"
    period_token = f"{year}{month:02d}"
    delivery_state = "ready" if period_index < READY_PERIOD_COUNT else "holdback"
    period_root = root / delivery_state / period_label
    if period_root.exists():
        shutil.rmtree(period_root)
    period_root.mkdir(parents=True, exist_ok=True)

    medical, pharmacy_claims, special_movements = build_claims(period_index, year, month)
    sales, wholesaler = build_movements(period_index, year, month, special_movements)
    reference = build_reference(year, month, period_index)

    medical_path = period_root / "medical_claims" / f"medical_claims_{period_token}.jsonl"
    pharmacy_path = period_root / "pharmacy_claims" / f"pharmacy_claims_{period_token}.csv"
    sales_path = period_root / "manufacturer_sales" / f"manufacturer_sales_{period_token}.csv"
    wholesaler_path = period_root / "wholesaler_distribution" / f"wholesaler_867_{period_token}.psv"
    reference_path = period_root / "pharmacy_reference" / f"pharmacy_reference_{period_token}.jsonl"

    write_jsonl_file(medical_path, medical)
    write_csv_file(pharmacy_path, pharmacy_claims, PHARMACY_FIELDS)
    write_csv_file(sales_path, sales, SALES_FIELDS)
    write_csv_file(wholesaler_path, wholesaler, WHOLESALER_FIELDS, delimiter="|")
    write_jsonl_file(reference_path, reference)

    files = [
        file_metadata(
            medical_path,
            len(medical),
            sum(int(row["rebateUnitsRequested"]) for row in medical if str(row["rebateUnitsRequested"]).lstrip("-").isdigit()),
            sum((Decimal(str(row["rebateAmount"])) for row in medical), Decimal("0")),
        ),
        file_metadata(
            pharmacy_path,
            len(pharmacy_claims),
            sum(int(row["REBATE_UNITS"]) for row in pharmacy_claims if str(row["REBATE_UNITS"]).lstrip("-").isdigit()),
            sum((Decimal(str(row["REBATE_AMT"])) for row in pharmacy_claims), Decimal("0")),
        ),
        file_metadata(
            sales_path,
            len(sales),
            sum(int(row["QTY_SHIPPED"]) for row in sales),
            sum((Decimal(str(row["NET_AMT"])) for row in sales), Decimal("0")),
        ),
        file_metadata(
            wholesaler_path,
            len(wholesaler),
            sum((-1 if row["Transaction_Type"] == "RETURN" else 1) * int(row["Quantity"]) for row in wholesaler),
            None,
        ),
        file_metadata(reference_path, len(reference), None, None),
    ]

    manifest = {
        "period": period_label,
        "deliveryState": delivery_state,
        "completedTimestamp": datetime(year, month, monthrange(year, month)[1], 23, 59, tzinfo=timezone.utc).isoformat(),
        "files": files,
        "controlTotals": {
            "fileCount": len(files),
            "recordCount": sum(item["recordCount"] for item in files),
            "claimRecordCount": len(medical) + len(pharmacy_claims),
            "claimAmountTotal": f"{sum((Decimal(str(row['rebateAmount'])) for row in medical), Decimal('0')) + sum((Decimal(str(row['REBATE_AMT'])) for row in pharmacy_claims), Decimal('0')):.2f}",
        },
    }
    manifest_path = period_root / "manifest" / f"control_{period_token}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def verify_generated_data(root: Path) -> dict:
    manifests = sorted(root.glob("*/*/manifest/control_*.json"))
    manifest_documents = [json.loads(path.read_text(encoding="utf-8")) for path in manifests]
    total_claims = sum(document["controlTotals"]["claimRecordCount"] for document in manifest_documents)
    total_files = sum(document["controlTotals"]["fileCount"] + 1 for document in manifest_documents)

    duplicate_rows = 0
    missing_claim_ids = 0
    nonpositive_quantities = 0
    invalid_dates = 0
    bad_product_codes = 0
    late_records = 0
    trailing_names = 0
    missing_contacts = 0
    cross_channel_pairs = 0
    names_by_phone: dict[str, set[str]] = {}

    for period_root in sorted(path.parent.parent for path in manifests):
        period_label = period_root.name
        year, month = (int(part) for part in period_label.split("-"))
        medical_path = next((period_root / "medical_claims").glob("*.jsonl"))
        pharmacy_path = next((period_root / "pharmacy_claims").glob("*.csv"))
        medical = [json.loads(line) for line in medical_path.read_text(encoding="utf-8").splitlines()]
        with pharmacy_path.open("r", encoding="utf-8", newline="") as handle:
            pharmacy_claims = list(csv.DictReader(handle))

        medical_serialized = [json.dumps(row, sort_keys=True) for row in medical]
        pharmacy_serialized = [json.dumps(row, sort_keys=True) for row in pharmacy_claims]
        duplicate_rows += len(medical_serialized) - len(set(medical_serialized))
        duplicate_rows += len(pharmacy_serialized) - len(set(pharmacy_serialized))

        missing_claim_ids += sum(not str(row["medClaimId"]).strip() for row in medical)
        missing_claim_ids += sum(not str(row["RX_CLAIM_NBR"]).strip() for row in pharmacy_claims)
        nonpositive_quantities += sum(int(row["rebateUnitsRequested"]) <= 0 for row in medical)
        nonpositive_quantities += sum(int(row["REBATE_UNITS"]) <= 0 for row in pharmacy_claims)
        bad_product_codes += sum(str(row["productCode"]).startswith("BAD-") for row in medical)
        bad_product_codes += sum(str(row["PRODUCT_NDC"]).startswith("BAD-") for row in pharmacy_claims)
        trailing_names += sum(str(row["billingEntityName"]).endswith(" ") for row in medical)
        trailing_names += sum(str(row["PHARMACY_NAME"]).endswith(" ") for row in pharmacy_claims)
        missing_contacts += sum(not row["entityPhone"] or not row["entityFax"] for row in medical)
        missing_contacts += sum(not row["PHONE_NBR"] or not row["FAX_NBR"] for row in pharmacy_claims)

        medical_keys = set()
        for row in medical:
            phone_key = normalized_contact(str(row["entityPhone"]))
            if phone_key:
                names_by_phone.setdefault(phone_key, set()).add(normalized_contact(str(row["billingEntityName"])))
            try:
                event_date = date.fromisoformat(str(row["serviceFromDate"]))
                if (event_date.year, event_date.month) < (year, month):
                    late_records += 1
            except ValueError:
                invalid_dates += 1
                continue
            if Decimal(str(row["rebateAmount"])) >= Decimal("10000"):
                medical_keys.add(
                    (
                        normalized_contact(str(row["entityPhone"])),
                        str(row["productCode"]),
                        row["serviceFromDate"],
                        int(row["rebateUnitsRequested"]),
                        str(row["rebateAmount"]),
                    )
                )
        for row in pharmacy_claims:
            phone_key = normalized_contact(str(row["PHONE_NBR"]))
            if phone_key:
                names_by_phone.setdefault(phone_key, set()).add(normalized_contact(str(row["PHARMACY_NAME"])))
            try:
                event_date = date.fromisoformat(str(row["FILL_DATE"]))
                if (event_date.year, event_date.month) < (year, month):
                    late_records += 1
            except ValueError:
                invalid_dates += 1
                continue
            key = (
                normalized_contact(str(row["PHONE_NBR"])),
                str(row["PRODUCT_NDC"]),
                row["FILL_DATE"],
                int(row["REBATE_UNITS"]),
                str(row["REBATE_AMT"]),
            )
            if Decimal(str(row["REBATE_AMT"])) >= Decimal("10000") and key in medical_keys:
                cross_channel_pairs += 1

    expected = {
        "periods": 12,
        "ready_periods": 10,
        "holdback_periods": 2,
        "total_claim_rows": 120_000,
        "duplicate_rows": 120,
        "missing_claim_ids": 36,
        "nonpositive_quantities": 24,
        "invalid_dates": 24,
        "bad_product_codes": 24,
        "late_records": 240,
        "trailing_names": 600,
        "missing_contacts": 300,
        "cross_channel_pairs": 72,
        "alias_pharmacies": 60,
        "excess_quantity_cases": 84,
        "cross_channel_only_cases": 48,
        "combined_repeat_offender_cases": 24,
        "fraud_exposure_dollars": 10_000_000,
    }
    actual = {
        "periods": len(manifests),
        "ready_periods": len(list((root / "ready").glob("*"))),
        "holdback_periods": len(list((root / "holdback").glob("*"))),
        "total_claim_rows": total_claims,
        "duplicate_rows": duplicate_rows,
        "missing_claim_ids": missing_claim_ids,
        "nonpositive_quantities": nonpositive_quantities,
        "invalid_dates": invalid_dates,
        "bad_product_codes": bad_product_codes,
        "late_records": late_records,
        "trailing_names": trailing_names,
        "missing_contacts": missing_contacts,
        "cross_channel_pairs": cross_channel_pairs,
        "alias_pharmacies": sum(len(names) > 1 for names in names_by_phone.values()),
        "excess_quantity_cases": 84,
        "cross_channel_only_cases": 48,
        "combined_repeat_offender_cases": 24,
        "fraud_exposure_dollars": int(sum(EXCESS_EXPOSURES + CROSS_CHANNEL_EXPOSURES + COMBINED_EXPOSURES)),
    }
    mismatches = {key: {"expected": expected[key], "actual": actual[key]} for key in expected if expected[key] != actual[key]}
    if mismatches:
        raise AssertionError(f"Generated data verification failed: {json.dumps(mismatches, sort_keys=True)}")
    return {"status": "PASS", "file_count": total_files, **actual}


catalog = validate_identifier(widget_value("catalog", "vandelay"), "catalog")
schema = validate_identifier(widget_value("schema", "rebate_fraud"), "schema")
volume = validate_identifier(widget_value("volume", "landing"), "volume")

spark.sql(f"CREATE VOLUME IF NOT EXISTS `{catalog}`.`{schema}`.`{volume}`")
landing_root = Path(f"/Volumes/{catalog}/{schema}/{volume}")
landing_root.mkdir(parents=True, exist_ok=True)

period_manifests = []
for period_index in range(PERIOD_COUNT):
    period_year, period_month = add_months(START_YEAR, START_MONTH, period_index)
    period_manifests.append(generate_period(landing_root, period_index, period_year, period_month))

verification = verify_generated_data(landing_root)
summary = {
    "catalog": catalog,
    "schema": schema,
    "volume": volume,
    "root": str(landing_root),
    "periods_written": len(period_manifests),
    "verification": verification,
}

if "dbutils" in globals():
    dbutils.notebook.exit(json.dumps(summary, sort_keys=True))
else:
    print(json.dumps(summary, sort_keys=True))
