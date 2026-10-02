import streamlit as st
import pandas as pd
import ezdxf
import io
import zipfile
from collections import defaultdict

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GPS → AutoCAD DXF",
    page_icon="📐",
    layout="wide"
)

# =========================================================
# RTL / PERSIAN UI
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
}

.stApp {
    direction: rtl;
}

textarea,
input,
select {
    direction: rtl !important;
    text-align: right !important;
}

h1, h2, h3, h4 {
    text-align: right;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCTIONS
# =========================================================

def read_gps_file(uploaded_file):

    name = uploaded_file.name.lower()

    if name.endswith(".csv"):

        # Try UTF-8
        try:
            return pd.read_csv(uploaded_file)
        except:
            uploaded_file.seek(0)
            return pd.read_csv(
                uploaded_file,
                encoding="latin1"
            )

    elif name.endswith(".xlsx"):

        return pd.read_excel(uploaded_file)

    elif name.endswith(".txt"):

        uploaded_file.seek(0)

        try:
            return pd.read_csv(
                uploaded_file,
                sep=None,
                engine="python"
            )
        except:
            uploaded_file.seek(0)

            return pd.read_csv(
                uploaded_file,
                sep=r"\s+",
                engine="python"
            )

    else:

        raise ValueError(
            "فرمت فایل پشتیبانی نمی‌شود."
        )


def create_layer(doc, layer_name):

    if layer_name not in doc.layers:

        doc.layers.add(
            name=layer_name
        )


def sanitize_layer_name(name):

    name = str(name)

    replacements = {
        " ": "_",
        "/": "_",
        "\\": "_",
        ":": "_",
        "*": "_",
        "?": "_",
        '"': "_",
        "<": "_",
        ">": "_",
        "|": "_"
    }

    for a, b in replacements.items():

        name = name.replace(a, b)

    return name[:250]


def feature_to_layer(feature):

    mapping = {

        "مرز زمین":
            "LAND_BOUNDARY",

        "ساختمان":
            "BUILDING",

        "جاده":
            "ROAD",

        "دیوار":
            "WALL",

        "حصار":
            "FENCE",

        "درخت":
            "TREE",

        "تأسیسات":
            "UTILITY",

        "نقطه":
            "SURVEY_POINTS",

        "خط تراز":
            "CONTOUR",

        "سایر":
            "OTHER"
    }

    return mapping.get(
        feature,
        "OTHER"
    )


def build_dxf(data, point_col, x_col, y_col, z_col,
              code_col, feature_map, create_points,
              create_polylines, close_boundaries):

    # -----------------------------------------------------
    # Create DXF document
    # -----------------------------------------------------

    doc = ezdxf.new(
        "R2013"
    )

    doc.header[
        "$INSUNITS"
    ] = 6  # meters

    modelspace = doc.modelspace()

    # -----------------------------------------------------
    # Prepare layers
    # -----------------------------------------------------

    layers = [

        "LAND_BOUNDARY",
        "BUILDING",
        "ROAD",
        "WALL",
        "FENCE",
        "TREE",
        "UTILITY",
        "SURVEY_POINTS",
        "CONTOUR",
        "OTHER"
    ]

    for layer in layers:

        create_layer(
            doc,
            layer
        )

    # -----------------------------------------------------
    # Prepare records
    # -----------------------------------------------------

    records = []

    for i, row in data.iterrows():

        try:

            x = float(row[x_col])
            y = float(row[y_col])

            if z_col != "بدون ارتفاع":

                z = float(row[z_col])

            else:

                z = 0.0

        except:

            continue

        point_id = str(
            row[point_col]
        )

        if code_col != "بدون Code":

            code = str(
                row[code_col]
            )

        else:

            code = "UNKNOWN"

        feature = feature_map.get(
            code,
            "نقطه"
        )

        records.append({

            "id": point_id,
            "x": x,
            "y": y,
            "z": z,
            "code": code,
            "feature": feature
        })

    # -----------------------------------------------------
    # Draw points
    # -----------------------------------------------------

    if create_points:

        for r in records:

            layer = feature_to_layer(
                r["feature"]
            )

            modelspace.add_point(

                (
                    r["x"],
                    r["y"],
                    r["z"]
                ),

                dxfattribs={
                    "layer": layer
                }
            )

    # -----------------------------------------------------
    # Group points by feature
    # -----------------------------------------------------

    grouped = defaultdict(list)

    for r in records:

        grouped[
            r["feature"]
        ].append(r)

    # -----------------------------------------------------
    # Create polylines
    # -----------------------------------------------------

    if create_polylines:

        polyline_features = [

            "مرز زمین",
            "ساختمان",
            "جاده",
            "دیوار",
            "حصار",
            "خط تراز"
        ]

        for feature in polyline_features:

            if feature not in grouped:

                continue

            points = grouped[
                feature
            ]

            if len(points) < 2:

                continue

            coords = [

                (
                    p["x"],
                    p["y"],
                    p["z"]
                )

                for p in points
            ]

            layer = feature_to_layer(
                feature
            )

            close = False

            if feature == "مرز زمین":

                close = close_boundaries

            if feature == "ساختمان":

                close = True

            modelspace.add_polyline3d(
                coords,
                dxfattribs={
                    "layer": layer
                },
                close=close
            )

    return doc, records


# =========================================================
# HEADER
# =========================================================

st.title(
    "📐 تبدیل مستقیم GPS به AutoCAD DXF"
)

st.markdown(
    """
این برنامه فایل برداشت GPS/GNSS را دریافت می‌کند،
نقاط را دسته‌بندی می‌کند و مستقیماً فایل DXF تولید می‌کند.

**نیازی به نصب AutoCAD در Codespaces نیست.**
"""
)

st.divider()


# =========================================================
# FILE UPLOAD
# =========================================================

st.header(
    "📁 ۱. بارگذاری فایل GPS"
)

uploaded_file = st.file_uploader(

    "فایل GPS را انتخاب کنید",

    type=[
        "csv",
        "txt",
        "xlsx"
    ]
)

if uploaded_file is None:

    st.info(
        "فایل CSV، TXT یا Excel خود را بارگذاری کنید."
    )

    st.stop()


# =========================================================
# READ FILE
# =========================================================

try:

    df = read_gps_file(
        uploaded_file
    )

except Exception as e:

    st.error(
        f"خطا در خواندن فایل: {e}"
    )

    st.stop()


if len(df) == 0:

    st.error(
        "فایل فاقد داده است."
    )

    st.stop()


st.success(
    f"تعداد {len(df)} ردیف از فایل GPS خوانده شد."
)


# =========================================================
# PREVIEW
# =========================================================

st.header(
    "👁️ ۲. مشاهده اطلاعات GPS"
)

st.dataframe(
    df,
    use_container_width=True
)


# =========================================================
# COLUMN SELECTION
# =========================================================

st.header(
    "🧭 ۳. تعیین ستون‌های مختصات"
)

columns = list(
    df.columns
)

col1, col2 = st.columns(2)


with col1:

    point_col = st.selectbox(
        "🔢 شماره نقطه",
        columns
    )

    x_col = st.selectbox(
        "📍 X / Easting",
        columns
    )


with col2:

    y_col = st.selectbox(
        "📍 Y / Northing",
        columns
    )

    z_col = st.selectbox(
        "📏 Z / Elevation",
        ["بدون ارتفاع"] + columns
    )


code_col = st.selectbox(

    "🏷️ Code / Description",

    ["بدون Code"] + columns
)


# =========================================================
# BASIC CLEANING
# =========================================================

try:

    numeric_x = pd.to_numeric(
        df[x_col],
        errors="coerce"
    )

    numeric_y = pd.to_numeric(
        df[y_col],
        errors="coerce"
    )

except:

    st.error(
        "ستون‌های X و Y قابل تبدیل به عدد نیستند."
    )

    st.stop()


valid_count = (
    numeric_x.notna()
    & numeric_y.notna()
).sum()


st.info(
    f"تعداد نقاط دارای مختصات معتبر: {valid_count}"
)


# =========================================================
# CODE CLASSIFICATION
# =========================================================

st.header(
    "🏷️ ۴. دسته‌بندی عوارض"
)

if code_col != "بدون Code":

    codes = sorted(

        df[code_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()

    )

else:

    codes = ["UNKNOWN"]


feature_options = [

    "مرز زمین",
    "ساختمان",
    "جاده",
    "دیوار",
    "حصار",
    "درخت",
    "تأسیسات",
    "نقطه",
    "خط تراز",
    "سایر"
]


feature_map = {}


for code in codes:

    code_upper = code.upper()

    default_index = 7

    if (
        "BND" in code_upper
        or "BOUND" in code_upper
        or "مرز" in code
    ):

        default_index = 0

    elif (
        "BLDG" in code_upper
        or "BUILD" in code_upper
        or "BUILDING" in code_upper
    ):

        default_index = 1

    elif (
        "ROAD" in code_upper
        or "RD" == code_upper
    ):

        default_index = 2

    elif "WALL" in code_upper:

        default_index = 3

    elif "FENCE" in code_upper:

        default_index = 4

    elif "TREE" in code_upper:

        default_index = 5

    feature_map[code] = st.selectbox(

        f"Code = {code}",

        feature_options,

        index=default_index,

        key=f"feature_{code}"
    )


# =========================================================
# DXF OPTIONS
# =========================================================

st.header(
    "⚙️ ۵. تنظیمات DXF"
)

col1, col2, col3 = st.columns(3)


with col1:

    create_points = st.checkbox(

        "📍 ایجاد نقاط",

        value=True
    )


with col2:

    create_polylines = st.checkbox(

        "〰️ ایجاد Polyline",

        value=True
    )


with col3:

    close_boundaries = st.checkbox(

        "🔲 بستن مرز زمین",

        value=True
    )


project_name = st.text_input(

    "📋 نام فایل DXF",

    "GPS_Survey"
)


# =========================================================
# GENERATE DXF
# =========================================================

st.header(
    "🚀 ۶. تولید فایل AutoCAD"
)


if st.button(

    "📐 تولید DXF",

    type="primary",

    use_container_width=True
):

    try:

        doc, records = build_dxf(

            df,

            point_col,
            x_col,
            y_col,
            z_col,
            code_col,
            feature_map,
            create_points,
            create_polylines,
            close_boundaries
        )

        # -------------------------------------------------
        # Save DXF into memory
        # -------------------------------------------------

        dxf_buffer = io.StringIO()

        doc.write(
            dxf_buffer
        )

        dxf_bytes = dxf_buffer.getvalue().encode(
            "utf-8"
        )

        # -------------------------------------------------
        # Statistics
        # -------------------------------------------------

        st.success(
            f"✅ فایل DXF با موفقیت تولید شد. "
            f"تعداد نقاط پردازش‌شده: {len(records)}"
        )

        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        st.download_button(

            label="⬇️ دریافت فایل DXF",

            data=dxf_bytes,

            file_name=f"{project_name}.dxf",

            mime="application/dxf",

            use_container_width=True
        )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        summary = defaultdict(int)

        for r in records:

            summary[
                r["feature"]
            ] += 1

        st.subheader(
            "📊 خلاصه نقشه"
        )

        summary_df = pd.DataFrame(

            [
                {
                    "عارضه": k,
                    "تعداد نقاط": v
                }

                for k, v in summary.items()
            ]
        )

        st.dataframe(
            summary_df,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"خطا هنگام تولید DXF: {e}"
        )


# =========================================================
# INFORMATION
# =========================================================

st.divider()

st.info(
    """
📌 نکته:

این برنامه مختصات GPS را تغییر نمی‌دهد.

اگر فایل GPS شامل Code باشد، Code برای تعیین نوع عارضه
استفاده می‌شود.

برای مثال:

BND → مرز زمین
BLDG → ساختمان
ROAD → جاده
WALL → دیوار
TREE → درخت

ترتیب نقاط برای ترسیم Polyline نیز از ترتیب قرارگیری
ردیف‌های فایل GPS استفاده می‌شود.
"""
)