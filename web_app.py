import streamlit as st
import pandas as pd
import os
from app.services.data_service import DataService
from app.services.price_service import PriceService
from app.services.analytics_service import AnalyticsService
from app.services.user_service import UserService
from app.path_utils import resource_path

# --- Page Configuration ---
st.set_page_config(
    page_title="EVE Echoes Planetary Mining Optimizer",
    page_icon="🪐",
    layout="wide"
)

# --- User Authentication ---
user_service = UserService(user_file_path=resource_path("app/secure/users.json"))

if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
    st.session_state.username = None

def login_form():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if user_service.verify_user(username, password):
                st.session_state.authentication_status = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")

def registration_form():
    st.title("Register")
    
    # Load Privacy Policy
    try:
        with open(resource_path("PRIVACY_POLICY.md"), "r", encoding="utf-8") as f:
            privacy_policy_md = f.read()
    except:
        privacy_policy_md = "Privacy Policy: Your data is stored locally and securely. We do not share your information with third parties."
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("registration_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            st.markdown("### Privacy Policy")
            st.info("By registering, you agree to our Privacy Policy. Your data is stored securely and never shared with third parties.")
            
            privacy_policy_accepted = st.checkbox("I agree to the Privacy Policy")
                
            submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif not privacy_policy_accepted:
                    st.error("You must accept the Privacy Policy to register.")
                else:
                    success, message = user_service.register_user(username, password)
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials.")
                    else:
                        st.error(message)
    
    with col2:
        st.markdown("### 💰 Support")
        st.info("""
        **ISK Donations:**
        
        **lawrokhPL**
        
        in EVE Echoes
        
        Thank you! o7
        """)

# --- Main App Logic ---
def main_app():
    username = st.session_state.username
    
    # --- Load User Preferences ---
    if 'user_prefs' not in st.session_state:
        st.session_state.user_prefs = user_service.load_user_preferences(username)

    def save_prefs():
        """Callback to save preferences."""
        user_service.save_user_preferences(username, st.session_state.user_prefs)

    # --- Data Loading ---
    @st.cache_resource(show_spinner=f"Loading data for {username}...")
    def load_user_services(username):
        """Loads all necessary services for a given user."""
        # Use resource_path for executable compatibility
        user_data_root = resource_path(os.path.join("data", "user_data", username))
        data_path = resource_path(os.path.join("data", "eve_planets.parquet"))
        prices_path = os.path.join(user_data_root, "prices.json")
        mining_units_path = os.path.join(user_data_root, "mining_units.json")

        # Create user-specific directories if they don't exist
        os.makedirs(user_data_root, exist_ok=True)
        os.makedirs(os.path.join(user_data_root, "price_imports"), exist_ok=True)
        
        data_service = DataService(data_path, mining_units_path)
        data_service.load_data()
        
        price_service = PriceService(prices_path)
        analytics_service = AnalyticsService(data_service, price_service)
        
        return data_service, price_service, analytics_service

    data_service, price_service, analytics_service = load_user_services(username)

    # --- Sidebar ---
    with st.sidebar:
        st.title(f"Welcome, {username}")
        if st.button("Logout"):
            st.session_state.authentication_status = None
            st.session_state.username = None
            st.rerun()
        
        st.header("Filters")
        
        # --- Price File Selection in Sidebar ---
        imports_dir = os.path.join("data", "user_data", username, "price_imports")
        saved_imports = [f for f in os.listdir(imports_dir) if f.endswith(".csv")]
        
        price_options = ["Default"] + saved_imports
        selected_price_file = st.selectbox(
            "Select Price Set", 
            options=price_options,
            help="Temporarily load a different set of prices for analysis. To set a new default, use the Price Management tab."
        )

        if selected_price_file != "Default":
            try:
                file_path = os.path.join(imports_dir, selected_price_file)
                imported_df = pd.read_csv(file_path)
                if "resource" in imported_df.columns and "price" in imported_df.columns:
                    price_dict = pd.Series(imported_df.price.values, index=imported_df.resource).to_dict()
                    price_service.update_multiple_prices(price_dict)
                else:
                    st.warning(f"Invalid format in {selected_price_file}. Using default prices.")
                    price_service.load_prices() # Revert to default
            except Exception as e:
                st.error(f"Error loading {selected_price_file}: {e}")
                price_service.load_prices() # Revert to default
        else:
            price_service.load_prices() # Ensure default is loaded

        search_query = st.text_input("Search System, Constellation, or Region")
        
        all_resources_list = data_service.get_all_resources()
        selected_resources = st.multiselect("Resource", all_resources_list, key="resource_filter")

        regions = data_service.get_regions()
        selected_regions = st.multiselect("Region", regions, key="region_filter")
        
        if not selected_regions:
            constellations_list = data_service.get_constellations()
        else:
            constellations_list = data_service.get_constellations(selected_regions)
        selected_constellations = st.multiselect("Constellation", constellations_list, key="constellation_filter")

        if not selected_constellations:
            systems_list = data_service.get_systems()
        else:
            systems_list = data_service.get_systems(selected_constellations)
        selected_systems = st.multiselect("System", systems_list, key="system_filter")

        st.divider()
        st.header("Logistics Input")
        
        st.session_state.user_prefs['ship_cargo_capacity'] = st.number_input(
            "Ship Cargo Capacity (m³)", 
            min_value=0, 
            value=st.session_state.user_prefs.get('ship_cargo_capacity', 10000), 
            step=100,
            on_change=save_prefs,
            key='pref_ship_cargo'
        )
        st.session_state.user_prefs['planetary_storage_capacity'] = st.number_input(
            "Planetary Storage Capacity (m³)", 
            min_value=0, 
            value=st.session_state.user_prefs.get('planetary_storage_capacity', 920), 
            step=10,
            on_change=save_prefs,
            key='pref_planetary_storage'
        )
        
        st.divider()
        st.markdown("""
        ### 💰 Support Development
        **ISK Donations:**  
        **lawrokhPL** in EVE Echoes
        
        Thank you! o7
        """)

    # --- Master DataFrame Preparation ---
    master_df_key = f'master_df_{username}'
    if master_df_key not in st.session_state:
        all_planets = data_service.get_all_planets()
        resource_data = []
        for planet in all_planets:
            for resource in planet.resources:
                resource_data.append({
                    "id": f"{resource.planet_id}_{resource.resource}",
                    "System": planet.system,
                    "Constellation": planet.constellation,
                    "Region": planet.region,
                    "Planet": planet.name,
                    "Type": planet.planet_type.value,
                    "Resource": resource.resource,
                    "Richness": resource.richness.value,
                    "Output/h/unit": resource.output,
                    "obj": resource 
                })
        st.session_state[master_df_key] = pd.DataFrame(resource_data)

    master_df = st.session_state[master_df_key]

    # --- Main Page ---
    st.title("Planetary Resource Analysis")
    
    # --- Donation Section ---
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("""
            💰 **Support the Developer**
            
            If you find this tool helpful, please consider supporting the development 
            by sending ISK donations to:
            
            **lawrokhPL** 
            
            in EVE Echoes. Your support helps maintain and improve this calculator!
            
            Thank you for using the EVE Echoes Planetary Mining Optimizer! o7
            """)
    
    st.divider()

    # Filtering logic on the master dataframe
    filtered_df = master_df
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    if selected_constellations:
        filtered_df = filtered_df[filtered_df['Constellation'].isin(selected_constellations)]
    if selected_systems:
        filtered_df = filtered_df[filtered_df['System'].isin(selected_systems)]
    if search_query:
        query = search_query.lower()
        filtered_df = filtered_df[
            filtered_df['System'].str.lower().contains(query) |
            filtered_df['Constellation'].str.lower().contains(query) |
            filtered_df['Region'].str.lower().contains(query)
        ]
    if selected_resources:
        filtered_df = filtered_df[filtered_df['Resource'].isin(selected_resources)]

    # Prepare data for display
    # Perform calculations on the filtered dataframe for performance
    df = filtered_df.copy()
    
    # Update mining units from objects, as they can change
    df['Mining Units'] = df['obj'].apply(lambda r: r.mining_units)

    prices = price_service.get_all_prices()
    price_map = df['Resource'].map(prices).fillna(0)
    
    df["Value/h/unit"] = df["Output/h/unit"] * price_map
    df["Total Value/h"] = df["Value/h/unit"] * df["Mining Units"]
    
    if not df.empty:
        df = df.set_index("id")

    # Display Analysis Table with Data Editor
    st.info("You can directly edit the 'Mining Units' column below. Click the 'Update Mining Units' button to apply changes.")

    if not df.empty:
        column_config = {
            "id": None, # Ukryj kolumnę ID
            "Mining Units": st.column_config.NumberColumn(
                "Mining Units",
                help="Set the number of mining units for this resource.",
                min_value=0, step=1, format="%d"
            ),
             "Value/h/unit": st.column_config.NumberColumn(format="%.2f"),
            "Total Value/h": st.column_config.NumberColumn(format="%.2f"),
        }
        
        # Sortowanie i przygotowanie kolumn do wyświetlenia
        df_display = df.sort_values(by="Total Value/h", ascending=False)
        display_cols = ["Region", "Constellation", "System", "Planet", "Type", "Resource", "Richness", "Output/h/unit", "Mining Units", "Value/h/unit", "Total Value/h"]
        
        # Upewnij się, że wszystkie kolumny istnieją przed ich wyświetleniem
        final_display_cols = [col for col in display_cols if col in df_display.columns]

        st.data_editor(
            df_display[final_display_cols],
            column_config=column_config,
            use_container_width=True,
            key="data_editor",
            hide_index=True # Ukryj domyślny indeks numeryczny
        )

        _, button_col = st.columns([4, 1])
        with button_col:
            if st.button("Update Mining Units"):
                if "data_editor" in st.session_state and st.session_state.data_editor.get("edited_rows"):
                    edited_rows = st.session_state.data_editor["edited_rows"]
                    changes_made = False
                    
                    for row_index, changes in edited_rows.items():
                        if "Mining Units" in changes:
                            resource_id = df_display.index[row_index]
                            new_units_val = changes["Mining Units"]
                            
                            try:
                                new_units = int(new_units_val)
                            except (ValueError, TypeError):
                                new_units = 0 # Domyślnie 0, jeśli dane wejściowe są nieprawidłowe (np. puste)
                            
                            resource_obj = df.loc[resource_id, 'obj']
                            
                            if resource_obj.mining_units != new_units:
                                resource_obj.mining_units = new_units
                                changes_made = True
                    
                    if changes_made:
                        data_service.save_mining_units()
                        data_service.update_dataframe_mining_units()
                        st.toast("Jednostki wydobywcze zaktualizowane!", icon="✅")
                        st.session_state.data_editor["edited_rows"] = {} # Wyczyść stan edytora
                        st.rerun()
                    else:
                        st.toast("Nie wykryto żadnych zmian w jednostkach wydobywczych.", icon="🤷")
                else:
                    st.toast("Brak zmian do zaktualizowania.", icon="ℹ️")
    else:
        st.info("No data to display for the selected filters.")


    # --- Tabs for other functionalities ---
    tab1, tab2, tab3 = st.tabs(["Summaries", "Price Management", "Data Visualization"])

    with tab1:
        st.header("Income & Logistics Summaries")

        # --- Tax Input ---
        st.session_state.user_prefs['tax_rate'] = st.number_input(
            "Broker/Transaction Tax (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.user_prefs.get('tax_rate', 8.0),
            step=0.1,
            format="%.2f",
            help="Enter your total tax rate (Broker Fee + Sales Tax) as a percentage.",
            on_change=save_prefs,
            key='pref_tax_rate'
        )

        # Create a single summary dataframe for all calculations
        summary_df = df[df['Mining Units'] > 0].copy()

        if not summary_df.empty:
            # --- CALCULATIONS (GROSS) ---
            summary_df['Gross Daily Income'] = summary_df['Total Value/h'] * 24
            summary_df['Gross Weekly Income'] = summary_df['Total Value/h'] * 24 * 7
            summary_df['Gross Monthly Income'] = summary_df['Total Value/h'] * 24 * 30
            
            # --- CALCULATIONS (NET) ---
            tax_rate = st.session_state.user_prefs.get('tax_rate', 8.0)
            tax_multiplier = 1 - (tax_rate / 100)
            summary_df['Net Daily Income'] = summary_df['Gross Daily Income'] * tax_multiplier
            summary_df['Net Weekly Income'] = summary_df['Gross Weekly Income'] * tax_multiplier
            summary_df['Net Monthly Income'] = summary_df['Gross Monthly Income'] * tax_multiplier

            # Volume
            RESOURCE_UNIT_VOLUME = 0.01  # m3
            summary_df['Hourly Volume (m3)'] = summary_df['Output/h/unit'] * summary_df['Mining Units'] * RESOURCE_UNIT_VOLUME

            # --- DISPLAY INCOME ---
            st.subheader("Income Summary")
            income_display_cols = ["Region", "Constellation", "System", "Planet", "Resource", "Mining Units", "Net Daily Income"]
            display_income_df = summary_df[income_display_cols].copy()
            # Format for display
            display_income_df["Net Daily Income"] = display_income_df["Net Daily Income"].map('{:,.2f}'.format)
            
            st.dataframe(display_income_df.sort_values(by="Net Daily Income", key=lambda x: pd.to_numeric(x.str.replace(',','')), ascending=False), use_container_width=True)
            
            # Totals
            total_net_daily = summary_df['Net Daily Income'].sum()
            total_net_weekly = summary_df['Net Weekly Income'].sum()
            total_net_monthly = summary_df['Net Monthly Income'].sum()
            
            i_col1, i_col2, i_col3 = st.columns(3)
            i_col1.metric("Total Net Daily Income", f"{total_net_daily:,.2f} ISK")
            i_col2.metric("Total Net Weekly Income", f"{total_net_weekly:,.2f} ISK")
            i_col3.metric("Total Net Monthly Income", f"{total_net_monthly:,.2f} ISK")

            st.divider()

            # --- FINAL PROFIT CALCULATION ---
            st.subheader("Final Profit Summary")
            
            st.session_state.user_prefs['pos_cost'] = st.number_input(
                "Corporation POS Cost (Monthly)",
                min_value=0,
                value=st.session_state.user_prefs.get('pos_cost', 1500000000),
                step=1000000,
                format="%d",
                help="Enter the total monthly cost for maintaining your Corporation POS.",
                on_change=save_prefs,
                key='pref_pos_cost'
            )

            pos_cost = st.session_state.user_prefs.get('pos_cost', 1500000000)
            final_monthly_profit = total_net_monthly - pos_cost

            f_col1, f_col2, f_col3 = st.columns(3)
            f_col1.metric("Net Monthly Income", f"{total_net_monthly:,.2f} ISK")
            f_col2.metric("Corporation POS Cost", f"{pos_cost:,.2f} ISK", delta_color="inverse")
            f_col3.metric("Final Monthly Profit", f"{final_monthly_profit:,.2f} ISK")


            st.divider()

            # --- DISPLAY LOGISTICS ---
            st.subheader("Logistics Summary")
            
            # --- Planetary Storage Fill Time (per Planet) ---
            st.markdown("#### Planetary Storage")
            if st.session_state.user_prefs['planetary_storage_capacity'] > 0:
                planet_volume_summary = summary_df.groupby(['System', 'Planet'])['Hourly Volume (m3)'].sum().reset_index()
                planet_volume_summary = planet_volume_summary[planet_volume_summary['Hourly Volume (m3)'] > 0]

                if not planet_volume_summary.empty:
                    planet_volume_summary['Time to Fill (hours)'] = st.session_state.user_prefs['planetary_storage_capacity'] / planet_volume_summary['Hourly Volume (m3)']
                    
                    display_planet_summary = planet_volume_summary.copy()
                    display_planet_summary['Hourly Volume (m3)'] = display_planet_summary['Hourly Volume (m3)'].map('{:,.2f}'.format)
                    display_planet_summary['Time to Fill (hours)'] = display_planet_summary['Time to Fill (hours)'].map('{:,.2f}'.format)
                    
                    st.dataframe(
                        display_planet_summary[['System', 'Planet', 'Hourly Volume (m3)', 'Time to Fill (hours)']],
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("Set planetary storage capacity to see fill times.")

            # --- Transport Summary ---
            st.markdown("#### Transport")
            if st.session_state.user_prefs['ship_cargo_capacity'] > 0:
                total_hourly_volume = summary_df['Hourly Volume (m3)'].sum()
                total_daily_volume = total_hourly_volume * 24

                collection_frequency_days = st.session_state.user_prefs['ship_cargo_capacity'] / total_daily_volume if total_daily_volume > 0 else float('inf')

                def format_frequency(days):
                    if days == float('inf'): return "N/A"
                    total_seconds = int(days * 24 * 3600)
                    if total_seconds <= 0: return "N/A"
                    d = total_seconds // 86400; h = (total_seconds % 86400) // 3600; m = (total_seconds % 3600) // 60
                    parts = []
                    if d > 0: parts.append(f"{d}d")
                    if h > 0: parts.append(f"{h}h")
                    if m > 0: parts.append(f"{m}m")
                    return " ".join(parts) if parts else "< 1m"
                
                frequency_str = format_frequency(collection_frequency_days)

                l_col1, l_col2, l_col3 = st.columns(3)
                l_col1.metric("Ship Cargo", f"{st.session_state.user_prefs['ship_cargo_capacity']:,.0f} m³")
                l_col2.metric("Total Daily Volume", f"{total_daily_volume:,.2f} m³")
                l_col3.metric("Collection Frequency", f"Every {frequency_str}")
            else:
                st.info("Set ship cargo capacity to see transport summary.")

        else:
            st.info("Assign mining units to see income and logistics summaries.")

    with tab2:
        st.header("Price Management")

        # --- Top Section: Import, Export, Load ---
        st.subheader("Manage Price Files")

        # Export Button
        prices_df = pd.DataFrame(price_service.get_all_prices().items(), columns=["resource", "price"])
        st.download_button(
            label="Export Current Prices to CSV",
            data=prices_df.to_csv(index=False).encode('utf-8'),
            file_name="current_prices.csv",
            mime="text/csv",
        )

        # Import Uploader
        uploaded_file = st.file_uploader("Upload a new price file to set as default", type="csv")
        if uploaded_file is not None:
            try:
                new_prices_df = pd.read_csv(uploaded_file)
                if "resource" in new_prices_df.columns and "price" in new_prices_df.columns:
                    file_path = os.path.join("data", "user_data", username, "price_imports", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    price_dict = pd.Series(new_prices_df.price.values, index=new_prices_df.resource).to_dict()
                    price_service.update_multiple_prices(price_dict)
                    price_service.save_prices()
                    st.success(f"Successfully imported and set {uploaded_file.name} as default prices.")
                    st.rerun()
                else:
                    st.error("Invalid CSV format. Please ensure it has 'resource' and 'price' columns.")
            except Exception as e:
                st.error(f"An error occurred during import: {e}")

        # Load from Saved
        imports_dir = os.path.join("data", "user_data", username, "price_imports")
        saved_imports = [f for f in os.listdir(imports_dir) if f.endswith(".csv")]
        
        if saved_imports:
            selected_import = st.selectbox("Or load a saved file to set as default:", options=["-"] + saved_imports)
            if selected_import != "-":
                if st.button(f"Load: {selected_import}"):
                    try:
                        file_path = os.path.join(imports_dir, selected_import)
                        imported_df = pd.read_csv(file_path)
                        if "resource" in imported_df.columns and "price" in imported_df.columns:
                            price_dict = pd.Series(imported_df.price.values, index=imported_df.resource).to_dict()
                            price_service.update_multiple_prices(price_dict)
                            price_service.save_prices()
                            st.success(f"Successfully set {selected_import} as default prices.")
                            st.rerun()
                        else:
                            st.error("Invalid CSV format in the selected file.")
                    except Exception as e:
                        st.error(f"An error occurred while loading the file: {e}")

        st.divider()

        # --- Bottom Section: Edit Individual Prices in 3 columns ---
        st.subheader("Edit Individual Prices")
        all_prices = price_service.get_all_prices()
        
        if not all_prices:
            st.warning("No prices found. Please import a price file to enable editing.")
        else:
            with st.form("edit_prices_form"):
                updated_prices = {}
                sorted_resources = sorted(all_prices.keys())
                
                cols = st.columns(3)
                
                for i, resource_name in enumerate(sorted_resources):
                    with cols[i % 3]:
                        price = all_prices.get(resource_name, 0.0)
                        updated_prices[resource_name] = st.number_input(
                            label=resource_name,
                            value=float(price),
                            format="%.2f",
                            key=f"price_{resource_name}"
                        )
                
                submitted = st.form_submit_button("Save Edited Prices as Default")
                if submitted:
                    price_service.update_multiple_prices(updated_prices)
                    price_service.save_prices()
                    price_service.load_prices()  # Przeładuj ceny z pliku
                    st.success("Prices saved successfully as default!")
                    st.rerun()

    with tab3:
        st.header("Price Trend Analysis")
        st.info(
            "This tool visualizes price changes over time based on your imported CSV files. "
            "For best results, ensure your filenames contain the date in **YYYY-MM-DD** format (e.g., `prices_2024-07-31.csv`) "
            "and each file contains `resource`, `buy`, `sell`, and `average` columns."
        )

        history_df = price_service.get_price_history(username)

        if history_df.empty:
            st.warning("No valid historical price files found. Please upload price files in the 'Price Management' tab.")
        else:
            all_resources = sorted(history_df['resource'].unique())
            
            selected_resources = st.multiselect(
                "Select Resources to Display",
                options=all_resources,
                default=all_resources[:3] if len(all_resources) > 2 else all_resources
            )

            if not selected_resources:
                st.info("Please select at least one resource to see the price trends.")
            else:
                filtered_history = history_df[history_df['resource'].isin(selected_resources)]

                # --- Gross Price Charts ---
                st.subheader("Gross Prices (Before Tax)")
                chart_data_buy = filtered_history.pivot(index='date', columns='resource', values='buy')
                chart_data_sell = filtered_history.pivot(index='date', columns='resource', values='sell')
                chart_data_avg = filtered_history.pivot(index='date', columns='resource', values='average')

                st.line_chart(chart_data_buy)
                st.line_chart(chart_data_sell)
                st.line_chart(chart_data_avg)
                
                st.divider()

                # --- Net Price Summary & Charts ---
                tax_rate = st.session_state.user_prefs.get('tax_rate', 8.0)
                tax_multiplier = 1 - (tax_rate / 100)
                st.subheader(f"Net Prices Analysis (After {tax_rate:.2f}% Tax)")

                summary_data = []
                for resource in selected_resources:
                    resource_df = filtered_history[filtered_history['resource'] == resource].sort_values('date')
                    if len(resource_df) > 0:
                        last_row = resource_df.iloc[-1]
                        last_net_buy = last_row['buy'] * tax_multiplier
                        change = 0
                        
                        if len(resource_df) > 1:
                            prev_row = resource_df.iloc[-2]
                            prev_net_buy = prev_row['buy'] * tax_multiplier
                            change = last_net_buy - prev_net_buy
                        
                        summary_data.append({
                            "Resource": resource,
                            "Latest Net Buy Price": last_net_buy,
                            "Change vs Previous": change
                        })
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(
                    summary_df,
                    column_config={
                        "Latest Net Buy Price": st.column_config.NumberColumn(format="%.2f ISK"),
                        "Change vs Previous": st.column_config.NumberColumn(format="%.2f ISK")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # --- Net Price Charts ---
                net_history = filtered_history.copy()
                net_history['buy'] *= tax_multiplier
                net_history['sell'] *= tax_multiplier
                net_history['average'] *= tax_multiplier
                
                net_chart_data_buy = net_history.pivot(index='date', columns='resource', values='buy')
                net_chart_data_sell = net_history.pivot(index='date', columns='resource', values='sell')
                net_chart_data_avg = net_history.pivot(index='date', columns='resource', values='average')

                st.line_chart(net_chart_data_buy)
                st.line_chart(net_chart_data_sell)
                st.line_chart(net_chart_data_avg)


if st.session_state.authentication_status:
    main_app()
else:
    login_form()
    with st.expander("Don't have an account? Register here"):
        registration_form() 