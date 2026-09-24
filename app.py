import os
from datetime import datetime

import pandas as pd
import streamlit as st


# =========================================================
# 1. CẤU HÌNH ỨNG DỤNG
# =========================================================

st.set_page_config(
    page_title="Order Nhà Hàng",
    page_icon="🍽️",
    layout="wide"
)

# File lưu dữ liệu dùng chung
CSV_FILE = "history.csv"

# Mật khẩu Admin
ADMIN_PASSWORD = "123456"


# =========================================================
# 2. THỰC ĐƠN NHÀ HÀNG MR. BÌNH
# =========================================================

menu = {

    "Đồ ăn": {

        "Pizza Hải Sản": 150000,

        "Mì Ý Bò Bằm": 95000,

        "Burger Gà": 65000,

        "Salad Trộn": 50000,

        "Bít tết Bò Mỹ": 250000,

        "Sườn nướng BBQ": 180000,

        "Cánh gà chiên mắm": 75000,

        "Lẩu cá diêu hồng": 200000,

        "Lẩu Thái hải sản": 300000,

    },

    "Thức uống": {

        "Coca Cola": 20000,

        "Trà Đào Cam Sả": 35000,

        "Cà Phê Sữa": 25000,

        "Nước Suối": 10000,

        "Sinh tố Bơ": 45000,

        "Nước ép cam": 40000,

        "Mojito chanh dây": 55000,

        "Bia Heineken": 30000,

    }

}


# =========================================================
# 3. CÁC HÀM XỬ LÝ DỮ LIỆU
# =========================================================

def load_history():

    """
    Đọc dữ liệu lịch sử từ file CSV.
    Nếu chưa có file thì trả về danh sách rỗng.
    """

    if not os.path.exists(CSV_FILE):
        return []

    try:

        df = pd.read_csv(
            CSV_FILE,
            encoding="utf-8-sig"
        )

        if df.empty:
            return []

        return df.to_dict(
            orient="records"
        )

    except Exception:

        return []


def save_history(history):

    """
    Lưu toàn bộ lịch sử giao dịch vào CSV.
    """

    df = pd.DataFrame(history)

    df.to_csv(
        CSV_FILE,
        index=False,
        encoding="utf-8-sig"
    )


def format_money(value):

    """
    Định dạng tiền Việt Nam.
    """

    return f"{float(value):,.0f} VNĐ"


def calculate_order(order):

    """
    Tính tổng tiền, giảm giá và số tiền thanh toán.
    """

    tam_tinh = sum(
        item["Thành tiền"]
        for item in order.values()
    )

    # Giảm 5% nếu hóa đơn trên 1 triệu
    giam_gia = (
        tam_tinh * 0.05
        if tam_tinh > 1000000
        else 0
    )

    tong_thanh_toan = (
        tam_tinh - giam_gia
    )

    return (
        tam_tinh,
        giam_gia,
        tong_thanh_toan
    )


# =========================================================
# 4. KHỞI TẠO SESSION STATE
# =========================================================

if "order_dict" not in st.session_state:

    st.session_state.order_dict = {}


if "history" not in st.session_state:

    st.session_state.history = load_history()


if "admin_logged_in" not in st.session_state:

    st.session_state.admin_logged_in = False


# =========================================================
# 5. SIDEBAR - THANH ĐIỀU HƯỚNG
# =========================================================

st.sidebar.title("🍽️ NHÀ HÀNG MR. BÌNH")

st.sidebar.caption(
    "Hệ thống Order & Quản lý doanh thu"
)

page = st.sidebar.radio(
    "📌 Chọn trang hệ thống",
    [
        "🛒 Order",
        "🔐 Admin"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "💡 Hóa đơn trên 1.000.000 VNĐ "
    "được giảm 5%."
)


# =========================================================
# 6. TRANG ORDER
# =========================================================

if page == "🛒 Order":

    st.title(
        "🍽️ HỆ THỐNG ORDER NHÀ HÀNG MR. BÌNH"
    )

    st.caption(
        "Ghi nhận order nhanh chóng và chính xác "
        "theo thời gian thực"
    )

    col1, col2 = st.columns(
        [1, 1.3]
    )


    # -----------------------------------------------------
    # 6.1 CHỌN MÓN
    # -----------------------------------------------------

    with col1:

        st.subheader(
            "🍴 Chọn món"
        )

        table_number = st.selectbox(
            "🪑 Chọn số bàn",
            [
                f"Bàn {i}"
                for i in range(1, 21)
            ]
        )

        category = st.selectbox(
            "📂 Chọn loại",
            list(menu.keys())
        )

        item = st.selectbox(
            "🍽️ Chọn món",
            list(
                menu[category].keys()
            )
        )

        price = menu[category][item]

        st.write(
            f"**Đơn giá:** "
            f"{format_money(price)}"
        )

        quantity = st.number_input(
            "🔢 Số lượng",
            min_value=1,
            value=1,
            step=1
        )

        if st.button(
            "➕ Thêm vào giỏ",
            use_container_width=True
        ):

            # Nếu món đã tồn tại
            if item in st.session_state.order_dict:

                st.session_state.order_dict[item][
                    "Số lượng"
                ] += quantity

                st.session_state.order_dict[item][
                    "Thành tiền"
                ] = (
                    st.session_state.order_dict[item][
                        "Số lượng"
                    ] * price
                )

                st.session_state.order_dict[item][
                    "Bàn"
                ] = table_number

            # Nếu món chưa tồn tại
            else:

                st.session_state.order_dict[item] = {

                    "Bàn": table_number,

                    "Tên món": item,

                    "Đơn giá": price,

                    "Số lượng": quantity,

                    "Thành tiền": (
                        price * quantity
                    )

                }

            st.success(
                f"Đã thêm {item} vào giỏ!"
            )

            st.rerun()


    # -----------------------------------------------------
    # 6.2 GIỎ HÀNG
    # -----------------------------------------------------

    with col2:

        st.subheader(
            "🛒 Giỏ hàng hiện tại"
        )

        if st.session_state.order_dict:

            df = pd.DataFrame.from_dict(
                st.session_state.order_dict,
                orient="index"
            )

            st.dataframe(
                df[
                    [
                        "Bàn",
                        "Tên món",
                        "Đơn giá",
                        "Số lượng",
                        "Thành tiền"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            tam_tinh, giam_gia, tong_thanh_toan = (
                calculate_order(
                    st.session_state.order_dict
                )
            )

            st.markdown("---")

            st.write(
                f"**Tạm tính:** "
                f"{format_money(tam_tinh)}"
            )

            if giam_gia > 0:

                st.write(
                    f"**Giảm giá 5%:** "
                    f"-{format_money(giam_gia)}"
                )

            else:

                st.write(
                    "**Giảm giá:** 0 VNĐ"
                )

            st.metric(
                "💰 TỔNG THANH TOÁN",
                format_money(
                    tong_thanh_toan
                )
            )

            col_btn1, col_btn2 = st.columns(2)


            # -------------------------------------------------
            # THANH TOÁN
            # -------------------------------------------------

            with col_btn1:

                if st.button(
                    "💳 Thanh toán",
                    use_container_width=True
                ):

                    now_str = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Tạo mã hóa đơn
                    invoice_id = (
                        datetime.now().strftime(
                            "%Y%m%d%H%M%S%f"
                        )
                    )

                    # Lưu từng món
                    for row in (
                        st.session_state.order_dict.values()
                    ):

                        st.session_state.history.append(

                            {

                                "Mã hóa đơn":
                                    invoice_id,

                                "Thời gian":
                                    now_str,

                                "Bàn":
                                    row["Bàn"],

                                "Tên món":
                                    row["Tên món"],

                                "Số lượng":
                                    row["Số lượng"],

                                "Thành tiền":
                                    row["Thành tiền"],

                                "Giảm giá":
                                    giam_gia,

                                "Tổng thanh toán":
                                    tong_thanh_toan

                            }

                        )

                    try:

                        save_history(
                            st.session_state.history
                        )

                        st.success(
                            "✅ Thanh toán thành công! "
                            "Dữ liệu đã được lưu."
                        )

                        st.session_state.order_dict = {}

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Lỗi lưu dữ liệu: {e}"
                        )


            # -------------------------------------------------
            # XÓA GIỎ
            # -------------------------------------------------

            with col_btn2:

                if st.button(
                    "🗑️ Xóa toàn bộ giỏ",
                    use_container_width=True
                ):

                    st.session_state.order_dict = {}

                    st.rerun()

        else:

            st.info(
                "🛒 Giỏ hàng đang trống. "
                "Hãy chọn món bên trái để lên đơn."
            )


# =========================================================
# 7. TRANG ADMIN
# =========================================================

elif page == "🔐 Admin":

    st.title(
        "🔐 TRANG QUẢN TRỊ & PHÂN TÍCH DOANH THU"
    )


    # =====================================================
    # 7.1 ĐĂNG NHẬP ADMIN
    # =====================================================

    if not st.session_state.admin_logged_in:

        with st.form(
            "admin_login_form"
        ):

            password = st.text_input(
                "🔑 Nhập mật khẩu quản trị",
                type="password"
            )

            login_submitted = (
                st.form_submit_button(
                    "🚪 Đăng nhập",
                    use_container_width=True
                )
            )

            if login_submitted:

                if password == ADMIN_PASSWORD:

                    st.session_state.admin_logged_in = True

                    st.success(
                        "Đăng nhập thành công!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Mật khẩu không chính xác!"
                    )

        st.warning(
            "Vui lòng nhập mật khẩu "
            "để xem dữ liệu kinh doanh."
        )

        st.stop()


    # =====================================================
    # 7.2 HEADER ADMIN
    # =====================================================

    col_header_title, col_header_btn = st.columns(
        [4, 1]
    )

    with col_header_title:

        st.success(
            "✅ Xác thực quyền Quản trị viên thành công!"
        )

    with col_header_btn:

        if st.button(
            "🚪 Đăng xuất",
            use_container_width=True
        ):

            st.session_state.admin_logged_in = False

            st.rerun()


    # =====================================================
    # 7.3 CÁC TAB ADMIN
    # =====================================================

    tab1, tab2, tab3 = st.tabs(

        [

            "📋 Danh sách thực đơn",

            "💰 Doanh thu & Nhật ký giao dịch",

            "📊 Thống kê & Phân tích REAL-TIME"

        ]

    )


    # =====================================================
    # TAB 1 - MENU
    # =====================================================

    with tab1:

        st.subheader(
            "📋 Menu hiện hành của nhà hàng"
        )

        data = []

        for category_name in menu:

            for item_name, price in (
                menu[category_name].items()
            ):

                data.append(

                    [

                        category_name,

                        item_name,

                        price

                    ]

                )

        df_menu = pd.DataFrame(

            data,

            columns=[

                "Phân loại",

                "Tên món",

                "Đơn giá (VNĐ)"

            ]

        )

        st.dataframe(

            df_menu.style.format(
                {
                    "Đơn giá (VNĐ)":
                        "{:,.0f} VNĐ"
                }
            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # TAB 2 - DOANH THU
    # =====================================================

    with tab2:

        st.subheader(
            "💰 Doanh thu & Hóa đơn thực tế"
        )

        # Đọc trực tiếp từ CSV
        if os.path.exists(CSV_FILE):

            try:

                df_history = pd.read_csv(
                    CSV_FILE,
                    encoding="utf-8-sig"
                )

            except Exception:

                df_history = pd.DataFrame()

        else:

            df_history = pd.DataFrame()


        if not df_history.empty:

            # Chuyển kiểu số
            df_history["Số lượng"] = pd.to_numeric(
                df_history["Số lượng"],
                errors="coerce"
            ).fillna(0)

            df_history["Thành tiền"] = pd.to_numeric(
                df_history["Thành tiền"],
                errors="coerce"
            ).fillna(0)


            # -------------------------------------------------
            # DOANH THU
            # -------------------------------------------------

            if "Mã hóa đơn" in df_history.columns:

                invoice_df = (
                    df_history
                    .drop_duplicates(
                        subset=["Mã hóa đơn"]
                    )
                )

                tong_doanh_thu = (
                    invoice_df[
                        "Tổng thanh toán"
                    ].sum()
                )

                so_hoa_don = len(
                    invoice_df
                )

            else:

                tong_doanh_thu = (
                    df_history[
                        "Thành tiền"
                    ].sum()
                )

                so_hoa_don = len(
                    df_history
                )


            so_luong_mon = (
                df_history[
                    "Số lượng"
                ].sum()
            )


            col_met1, col_met2, col_met3 = (
                st.columns(3)
            )


            col_met1.metric(

                "💰 Tổng doanh thu",

                format_money(
                    tong_doanh_thu
                )

            )


            col_met2.metric(

                "🧾 Số hóa đơn",

                f"{so_hoa_don}"

            )


            col_met3.metric(

                "🍽️ Số lượng món",

                f"{int(so_luong_mon)} phần"

            )


            st.markdown("---")


            # =================================================
            # DOANH THU THEO NGÀY
            # =================================================

            st.subheader(
                "📅 Thống kê doanh thu theo ngày"
            )

            df_history["Thời gian"] = (
                pd.to_datetime(
                    df_history["Thời gian"],
                    errors="coerce"
                )
            )

            df_history["Ngày"] = (
                df_history["Thời gian"].dt.date
            )


            if "Mã hóa đơn" in df_history.columns:

                df_daily_revenue = (

                    df_history
                    .drop_duplicates(
                        subset=["Mã hóa đơn"]
                    )
                    .groupby("Ngày")[
                        "Tổng thanh toán"
                    ]
                    .sum()
                    .reset_index()

                )

            else:

                df_daily_revenue = (

                    df_history
                    .groupby("Ngày")[
                        "Thành tiền"
                    ]
                    .sum()
                    .reset_index()

                )


            df_daily_revenue.columns = [

                "Ngày",

                "Doanh thu (VNĐ)"

            ]


            col_chart_day, col_table_day = (
                st.columns([1.5, 1])
            )


            with col_chart_day:

                st.write(
                    "**📊 Biểu đồ doanh thu hàng ngày:**"
                )

                st.bar_chart(

                    df_daily_revenue.set_index(
                        "Ngày"
                    )[
                        "Doanh thu (VNĐ)"
                    ]

                )


            with col_table_day:

                st.write(
                    "**📋 Bảng doanh thu:**"
                )

                st.dataframe(

                    df_daily_revenue.style.format(

                        {

                            "Doanh thu (VNĐ)":
                                "{:,.0f} VNĐ"

                        }

                    ),

                    use_container_width=True,

                    hide_index=True

                )


            st.markdown("---")


            # =================================================
            # LỊCH SỬ GIAO DỊCH
            # =================================================

            st.subheader(
                "🧾 Chi tiết lịch sử thanh toán"
            )

            columns_display = [

                "Thời gian",

                "Bàn",

                "Tên món",

                "Số lượng",

                "Thành tiền"

            ]

            st.dataframe(

                df_history[
                    columns_display
                ],

                use_container_width=True,

                hide_index=True

            )


            # Nút tải CSV

            csv_data = df_history.to_csv(
                index=False,
                encoding="utf-8-sig"
            )

            st.download_button(

                "⬇️ Tải dữ liệu CSV",

                data=csv_data,

                file_name="history_export.csv",

                mime="text/csv",

                use_container_width=True

            )


        else:

            st.info(
                "Hệ thống chưa ghi nhận "
                "bất kỳ giao dịch nào."
            )


    # =====================================================
    # TAB 3 - PHÂN TÍCH
    # =====================================================

    with tab3:

        st.subheader(
            "📊 Phân tích số liệu & Khung giờ vàng"
        )


        # Đọc dữ liệu mới nhất

        if os.path.exists(CSV_FILE):

            try:

                df_anal = pd.read_csv(
                    CSV_FILE,
                    encoding="utf-8-sig"
                )

            except Exception:

                df_anal = pd.DataFrame()

        else:

            df_anal = pd.DataFrame()


        if not df_anal.empty:

            # -------------------------------------------------
            # CHUYỂN KIỂU DỮ LIỆU
            # -------------------------------------------------

            df_anal["Thời gian"] = (
                pd.to_datetime(
                    df_anal["Thời gian"],
                    errors="coerce"
                )
            )

            df_anal["Số lượng"] = pd.to_numeric(
                df_anal["Số lượng"],
                errors="coerce"
            ).fillna(0)

            df_anal["Thành tiền"] = pd.to_numeric(
                df_anal["Thành tiền"],
                errors="coerce"
            ).fillna(0)

            df_anal["Giờ"] = (
                df_anal["Thời gian"].dt.hour
            )

            df_anal["Tháng-Năm"] = (
                df_anal["Thời gian"]
                .dt.strftime("%m/%Y")
            )


            # =================================================
            # 1. MÓN BÁN CHẠY NHẤT
            # =================================================

            seller_data = (

                df_anal
                .groupby("Tên món")[
                    "Số lượng"
                ]
                .sum()
                .sort_values(
                    ascending=False
                )

            )

            best_seller = (
                seller_data.index[0]
            )

            best_seller_qty = (
                seller_data.iloc[0]
            )


            # =================================================
            # 2. KHUNG GIỜ BÁN CHẠY
            # =================================================

            hourly_sales = (

                df_anal
                .groupby("Giờ")[
                    "Số lượng"
                ]
                .sum()

            )

            best_hour = (
                hourly_sales.idxmax()
            )

            best_hour_qty = (
                hourly_sales.max()
            )


            # =================================================
            # 3. THÁNG DOANH THU CAO NHẤT
            # =================================================

            if "Mã hóa đơn" in df_anal.columns:

                monthly_revenue = (

                    df_anal
                    .drop_duplicates(
                        subset=["Mã hóa đơn"]
                    )
                    .groupby("Tháng-Năm")[
                        "Tổng thanh toán"
                    ]
                    .sum()

                )

            else:

                monthly_revenue = (

                    df_anal
                    .groupby("Tháng-Năm")[
                        "Thành tiền"
                    ]
                    .sum()

                )


            best_month = (
                monthly_revenue.idxmax()
            )

            best_month_rev = (
                monthly_revenue.max()
            )


            # =================================================
            # KPI
            # =================================================

            col_kpi1, col_kpi2, col_kpi3 = (
                st.columns(3)
            )


            with col_kpi1:

                st.info(
                    "🔥 MÓN BÁN CHẠY NHẤT"
                )

                st.metric(

                    label=best_seller,

                    value=(
                        f"{int(best_seller_qty)} phần"
                    )

                )


            with col_kpi2:

                st.warning(
                    "⚡ KHUNG GIỜ BÁN CHẠY"
                )

                next_hour = (
                    (best_hour + 1) % 24
                )

                st.metric(

                    label=(
                        f"{best_hour:02d}:00 - "
                        f"{next_hour:02d}:00"
                    ),

                    value=(
                        f"{int(best_hour_qty)} phần"
                    )

                )


            with col_kpi3:

                st.success(
                    "🏆 THÁNG DOANH THU CAO NHẤT"
                )

                st.metric(

                    label=f"Tháng {best_month}",

                    value=format_money(
                        best_month_rev
                    )

                )


            st.markdown("---")


            # =================================================
            # PHÂN TÍCH TỪNG MÓN
            # =================================================

            st.write(
                "### 🍽️ Doanh thu & số lượng tiêu thụ từng món"
            )


            summary_mon = (

                df_anal
                .groupby("Tên món")
                .agg(

                    Số_lượng_bán=(
                        "Số lượng",
                        "sum"
                    ),

                    Doanh_thu=(
                        "Thành tiền",
                        "sum"
                    )

                )
                .reset_index()

                .sort_values(

                    by="Số_lượng_bán",

                    ascending=False

                )

            )


            col_chart1, col_table1 = (
                st.columns([1.5, 1])
            )


            with col_chart1:

                st.write(
                    "**📊 Tổng số lượng bán ra:**"
                )

                st.bar_chart(

                    summary_mon.set_index(
                        "Tên món"
                    )[
                        "Số_lượng_bán"
                    ]

                )


            with col_table1:

                st.write(
                    "**💰 Doanh thu từng món:**"
                )

                st.dataframe(

                    summary_mon.style.format(

                        {
                            "Doanh_thu":
                                "{:,.0f} VNĐ"
                        }

                    ),

                    use_container_width=True,

                    hide_index=True

                )


            st.markdown("---")


            # =================================================
            # PHÂN TÍCH KHUNG GIỜ
            # =================================================

            st.write(
                "### ⏰ Thống kê lượng bán theo khung giờ"
            )


            summary_gio = (

                df_anal
                .groupby("Giờ")
                .agg(

                    Số_lượng_món=(
                        "Số lượng",
                        "sum"
                    ),

                    Doanh_thu=(
                        "Thành tiền",
                        "sum"
                    )

                )
                .reset_index()

            )


            all_hours = pd.DataFrame(
                {
                    "Giờ":
                        range(24)
                }
            )


            summary_gio = (

                pd.merge(

                    all_hours,

                    summary_gio,

                    on="Giờ",

                    how="left"

                )

                .fillna(0)

            )


            col_chart2, col_info2 = (
                st.columns([1.5, 1])
            )


            with col_chart2:

                st.write(
                    "**📊 Lượng món bán theo từng giờ:**"
                )

                st.bar_chart(

                    summary_gio.set_index(
                        "Giờ"
                    )[
                        "Số_lượng_món"
                    ]

                )


            with col_info2:

                st.write(
                    "**⚡ Khung giờ bán chạy nhất:**"
                )

                st.markdown(

                    f"""
                    🔥 Hiện tại khung giờ bán
                    nhiều nhất là **{best_hour:02d}:00 -
                    {(best_hour + 1) % 24:02d}:00**.

                    Tổng số lượng:
                    **{int(best_hour_qty)} phần**
                    """
                )


                st.dataframe(

                    summary_gio[
                        summary_gio[
                            "Số_lượng_món"
                        ] > 0
                    ]

                    .style.format(

                        {
                            "Doanh_thu":
                                "{:,.0f} VNĐ"
                        }

                    ),

                    use_container_width=True,

                    hide_index=True

                )


            st.markdown("---")


            # =================================================
            # DOANH THU THEO THÁNG
            # =================================================

            st.write(
                "### 📈 Doanh thu bán hàng theo tháng"
            )


            if "Mã hóa đơn" in df_anal.columns:

                summary_thang = (

                    df_anal
                    .drop_duplicates(
                        subset=["Mã hóa đơn"]
                    )
                    .groupby("Tháng-Năm")
                    .agg(

                        Doanh_thu=(
                            "Tổng thanh toán",
                            "sum"
                        )

                    )
                    .reset_index()

                )

            else:

                summary_thang = (

                    df_anal
                    .groupby("Tháng-Năm")
                    .agg(

                        Doanh_thu=(
                            "Thành tiền",
                            "sum"
                        )

                    )
                    .reset_index()

                )


            col_chart3, col_table3 = (
                st.columns([1.5, 1])
            )


            with col_chart3:

                st.write(
                    "**📊 Biểu đồ doanh thu theo tháng:**"
                )

                st.bar_chart(

                    summary_thang.set_index(
                        "Tháng-Năm"
                    )[
                        "Doanh_thu"
                    ]

                )


            with col_table3:

                st.write(
                    "**📋 Tổng doanh thu từng tháng:**"
                )

                st.dataframe(

                    summary_thang.style.format(

                        {
                            "Doanh_thu":
                                "{:,.0f} VNĐ"
                        }

                    ),

                    use_container_width=True,

                    hide_index=True

                )


        else:

            st.info(
                "📭 Chưa có dữ liệu giao dịch "
                "để thống kê. Hãy tiến hành "
                "thanh toán một vài đơn hàng trước."
            )
