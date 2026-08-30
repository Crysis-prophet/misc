import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==================== 【1. 全局常量定义区】 ====================
# 先定义好两套数组的房间号，供后续所有配置和计算使用

# 最大等级
MAX_LEVEL = 175 # 最大等级
LEVEL_NUM = MAX_LEVEL + 1 # 等级范围：0级 到 最大等级

# 成长上下限
C_GROWTH_MIN = 1.0
C_GROWTH_MAX = 1.4

# 定义 5 种属性的索引常量
C_ATTR_CON = 0 # 体质
C_ATTR_MAG = 1 # 魔力
C_ATTR_STR = 2 # 力量
C_ATTR_ADJ = 3 # 耐力
C_ATTR_AGI = 4 # 敏捷
C_ATTR_NUM = 5 # 属性数量

# 初始属性上下限
C_INIT_ATTR_MIN = 10
C_INIT_ATTR_MAX = 50

# 初始属性数量
C_INIT_ATTR_NUM = 100

# 每级属性数量
C_LEVEL_ATTR_NUM = 5

# 定义 6 种资质的索引常量
C_APT_ATK = 0 # 攻击资质
C_APT_DEF = 1 # 防御资质
C_APT_CON = 2 # 体力资质
C_APT_MAG = 3 # 法力资质
C_APT_AGI = 4 # 速度资质
C_APT_DOD = 5 # 躲闪资质
C_APT_NUM = 6 # 资质数量

# 资质上下限
C_APT_ATK_MIN = 500
C_APT_ATK_MAX = 1800
C_APT_DEF_MIN = 500
C_APT_DEF_MAX = 1800
C_APT_CON_MIN = 1000
C_APT_CON_MAX = 7000
C_APT_MAG_MIN = 1000
C_APT_MAG_MAX = 3500
C_APT_AGI_MIN = 500
C_APT_AGI_MAX = 1800
C_APT_DOD_MIN = 500
C_APT_DOD_MAX = 1800

# ==================== 【2. 抽离的可配置数据区】 ====================
# 所有的属性、资质、甚至加点方案，全部使用刚刚定义的常量索引进行初始化

# --- 召唤兽 A 的配置初始化 ---
GROWTH_A = 1.167

INIT_APT_A = np.zeros(6)
INIT_APT_A[C_APT_ATK] = 1404  # 攻击资质
INIT_APT_A[C_APT_DEF] = 1150  # 防御资质
INIT_APT_A[C_APT_CON] = 3540  # 体力资质
INIT_APT_A[C_APT_MAG] = 2340  # 法力资质
INIT_APT_A[C_APT_AGI] = 1308  # 速度资质
INIT_APT_A[C_APT_DOD] = 1133  # 躲闪资质

INIT_ATTR_A = np.zeros(5)
INIT_ATTR_A[C_ATTR_CON] = 14  # 初始体质
INIT_ATTR_A[C_ATTR_MAG] = 30  # 初始魔力
INIT_ATTR_A[C_ATTR_STR] = 18  # 初始力量
INIT_ATTR_A[C_ATTR_ADJ] = 23  # 初始耐力
INIT_ATTR_A[C_ATTR_AGI] = 15  # 初始敏捷

PLAN_A = np.zeros(5)
PLAN_A[C_ATTR_STR] = 5  # 升级加点：5力全力加点


# --- 召唤兽 B 的配置初始化 ---
GROWTH_B = 1.19

INIT_APT_B = np.zeros(6)
INIT_APT_B[C_APT_ATK] = 1356
INIT_APT_B[C_APT_DEF] = 1265
INIT_APT_B[C_APT_CON] = 3570
INIT_APT_B[C_APT_MAG] = 2100
INIT_APT_B[C_APT_AGI] = 1332
INIT_APT_B[C_APT_DOD] = 1133

INIT_ATTR_B = np.zeros(5)
INIT_ATTR_B[C_ATTR_CON] = 28
INIT_ATTR_B[C_ATTR_MAG] = 25
INIT_ATTR_B[C_ATTR_STR] = 16
INIT_ATTR_B[C_ATTR_ADJ] = 13
INIT_ATTR_B[C_ATTR_AGI] = 18

PLAN_B = np.zeros(5)
PLAN_B[C_ATTR_STR] = 5  # 升级加点：5力全力加点


CONFIG_BEAST_A = {
    "name": "召唤兽 A (如：变异鬼将)",
    "growth": GROWTH_A,
    "aptitudes": INIT_APT_A,
    "initial_attrs": INIT_ATTR_A,
    "point_plan": PLAN_A
}

CONFIG_BEAST_B = {
    "name": "召唤兽 B (如：毗舍童子)",
    "growth": GROWTH_B,
    "aptitudes": INIT_APT_B,
    "initial_attrs": INIT_ATTR_B,
    "point_plan": PLAN_B
}


# ==================== 3. 页面基本配置 ====================
st.set_page_config(page_title="梦幻西游双召唤兽对比模拟器", layout="wide")
st.title("🦌 梦幻西游召唤兽全属性【双宠实时对比】模拟器")
st.markdown("在左侧边栏分别配置召唤兽参数，右侧将实时渲染对比曲线。")

# 设置 Matplotlib 支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


# ==================== 4. 侧边栏：从配置区加载并动态绑定 UI ====================

def validate_data(val, expect, greater_error, less_warning):
    if val > expect:
        st.sidebar.error(greater_error)
        st.stop() # 强行中断后续计算，保护系统不报错
    elif val < expect:
        st.sidebar.warning(less_warning)

# --- 召唤兽 A 侧边栏交互 ---
st.sidebar.markdown(f"### 🔵 {CONFIG_BEAST_A['name']} 配置")
growth_A = st.sidebar.slider("成长 (A)", C_GROWTH_MIN, C_GROWTH_MAX, CONFIG_BEAST_A["growth"], 0.005, format="%.3f", key="g_a")

col_apt_A1, col_apt_A2 = st.sidebar.columns(2)
apt_A = np.zeros(6)
with col_apt_A1:
    apt_A[C_APT_ATK] = st.number_input("攻击资质 (A)", C_APT_ATK_MIN, C_APT_ATK_MAX, int(CONFIG_BEAST_A["aptitudes"][C_APT_ATK]), 10, key="atk_a")
    apt_A[C_APT_CON] = st.number_input("体力资质 (A)", C_APT_CON_MIN, C_APT_CON_MAX, int(CONFIG_BEAST_A["aptitudes"][C_APT_CON]), 50, key="con_a")
    apt_A[C_APT_AGI] = st.number_input("速度资质 (A)", C_APT_AGI_MIN, C_APT_AGI_MAX, int(CONFIG_BEAST_A["aptitudes"][C_APT_AGI]), 10, key="agi_a")
with col_apt_A2:
    apt_A[C_APT_DEF] = st.number_input("防御资质 (A)", C_APT_DEF_MIN, C_APT_DEF_MAX, int(CONFIG_BEAST_A["aptitudes"][C_APT_DEF]), 10, key="def_a")
    apt_A[C_APT_MAG] = st.number_input("法力资质 (A)", C_APT_MAG_MIN, C_APT_MAG_MAX, int(CONFIG_BEAST_A["aptitudes"][C_APT_MAG]), 50, key="mag_a")
    apt_A[C_APT_DOD] = st.number_input("躲闪资质 (A)", C_APT_DOD_MIN, C_APT_DOD_MAX, int(CONFIG_BEAST_A["aptitudes"][C_APT_DOD]), 10, key="dod_a")

st.sidebar.markdown("#### 0级初始属性 (A)")
col_init_A1, col_init_A2 = st.sidebar.columns(2)
init_A = np.zeros(5)
with col_init_A1:
    init_A[C_ATTR_CON] = st.number_input("初始体质 (A)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_A["initial_attrs"][C_ATTR_CON]), key="con_init_a")
    init_A[C_ATTR_STR] = st.number_input("初始力量 (A)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_A["initial_attrs"][C_ATTR_STR]), key="str_init_a")
    init_A[C_ATTR_AGI] = st.number_input("初始敏捷 (A)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_A["initial_attrs"][C_ATTR_AGI]), key="agi_init_a")
with col_init_A2:
    init_A[C_ATTR_MAG] = st.number_input("初始魔力 (A)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_A["initial_attrs"][C_ATTR_MAG]), key="mag_init_a")
    init_A[C_ATTR_ADJ] = st.number_input("初始耐力 (A)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_A["initial_attrs"][C_ATTR_ADJ]), key="adj_init_a")
    
init_points_A = np.sum(init_A)
validate_data(init_points_A, C_INIT_ATTR_NUM,
              f"❌ 警告：A 的0级初始属性总数应为 {C_INIT_ATTR_NUM} 点！(当前 {init_points_A:.0f} 点)",
              f"❌ 警告：A 的0级初始属性总数应为 {C_INIT_ATTR_NUM} 点！(当前 {init_points_A:.0f} 点)")

st.sidebar.markdown("#### 每级加点分配 (A)")
col_plan_A1, col_plan_A2 = st.sidebar.columns(2)
plan_A_live = np.zeros(5, dtype=int)
with col_plan_A1:
    plan_A_live[C_ATTR_CON] = st.number_input("加点-体质 (A)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_A["point_plan"][C_ATTR_CON]), 1, key="p_con_a")
    plan_A_live[C_ATTR_STR] = st.number_input("加点-力量 (A)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_A["point_plan"][C_ATTR_STR]), 1, key="p_str_a")
    plan_A_live[C_ATTR_AGI] = st.number_input("加点-敏捷 (A)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_A["point_plan"][C_ATTR_AGI]), 1, key="p_agi_a")
with col_plan_A2:
    plan_A_live[C_ATTR_MAG] = st.number_input("加点-魔力 (A)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_A["point_plan"][C_ATTR_MAG]), 1, key="p_mag_a")
    plan_A_live[C_ATTR_ADJ] = st.number_input("加点-耐力 (A)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_A["point_plan"][C_ATTR_ADJ]), 1, key="p_adj_a")

total_points_A = np.sum(plan_A_live)
validate_data(total_points_A, C_LEVEL_ATTR_NUM,
              f"❌ 警告：A 的升级加点总数不能超过 {C_LEVEL_ATTR_NUM} 点！(当前 {total_points_A:.0f} 点)",
              f"⚠️ 提示：A 还有 {(C_LEVEL_ATTR_NUM - total_points_A):.0f} 点未分配")
    
st.sidebar.markdown("---")

# --- 召唤兽 B 侧边栏交互 ---
st.sidebar.markdown(f"### 🔴 {CONFIG_BEAST_B['name']} 配置")
growth_B = st.sidebar.slider("成长 (B)", C_GROWTH_MIN, C_GROWTH_MAX, CONFIG_BEAST_B["growth"], 0.005, format="%.3f", key="g_b")

col_apt_B1, col_apt_B2 = st.sidebar.columns(2)
apt_B = np.zeros(6)
with col_apt_B1:
    apt_B[C_APT_ATK] = st.number_input("攻击资质 (B)", C_APT_ATK_MIN, C_APT_ATK_MAX, int(CONFIG_BEAST_B["aptitudes"][C_APT_ATK]), 10, key="atk_b")
    apt_B[C_APT_CON] = st.number_input("体力资质 (B)", C_APT_CON_MIN, C_APT_CON_MAX, int(CONFIG_BEAST_B["aptitudes"][C_APT_CON]), 50, key="con_b")
    apt_B[C_APT_AGI] = st.number_input("速度资质 (B)", C_APT_AGI_MIN, C_APT_AGI_MAX, int(CONFIG_BEAST_B["aptitudes"][C_APT_AGI]), 10, key="agi_b")
with col_apt_B2:
    apt_B[C_APT_DEF] = st.number_input("防御资质 (B)", C_APT_DEF_MIN, C_APT_DEF_MAX, int(CONFIG_BEAST_B["aptitudes"][C_APT_DEF]), 10, key="def_b")
    apt_B[C_APT_MAG] = st.number_input("法力资质 (B)", C_APT_MAG_MIN, C_APT_MAG_MAX, int(CONFIG_BEAST_B["aptitudes"][C_APT_MAG]), 50, key="mag_b")
    apt_B[C_APT_DOD] = st.number_input("躲闪资质 (B)", C_APT_DOD_MIN, C_APT_DOD_MAX, int(CONFIG_BEAST_B["aptitudes"][C_APT_DOD]), 10, key="dod_b")

st.sidebar.markdown("#### 0级初始属性 (B)")
col_init_B1, col_init_B2 = st.sidebar.columns(2)
init_B = np.zeros(5)
with col_init_B1:
    init_B[C_ATTR_CON] = st.number_input("初始体质 (B)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_B["initial_attrs"][C_ATTR_CON]), key="con_init_b")
    init_B[C_ATTR_STR] = st.number_input("初始力量 (B)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_B["initial_attrs"][C_ATTR_STR]), key="str_init_b")
    init_B[C_ATTR_AGI] = st.number_input("初始敏捷 (B)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_B["initial_attrs"][C_ATTR_AGI]), key="agi_init_b")
with col_init_B2:
    init_B[C_ATTR_ADJ] = st.number_input("初始耐力 (B)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_B["initial_attrs"][C_ATTR_ADJ]), key="adj_init_b")
    init_B[C_ATTR_MAG] = st.number_input("初始魔力 (B)", C_INIT_ATTR_MIN, C_INIT_ATTR_MAX, int(CONFIG_BEAST_B["initial_attrs"][C_ATTR_MAG]), key="mag_init_b")

init_points_B = np.sum(init_B)
validate_data(init_points_B, C_INIT_ATTR_NUM,
              f"❌ 警告：B 的0级初始属性总数应为 {C_INIT_ATTR_NUM} 点！(当前 {init_points_B:.0f} 点)",
              f"❌ 警告：B 的0级初始属性总数应为 {C_INIT_ATTR_NUM} 点！(当前 {init_points_B:.0f} 点)")

st.sidebar.markdown("#### 每级加点分配 (B)")
col_plan_B1, col_plan_B2 = st.sidebar.columns(2)
plan_B_live = np.zeros(5, dtype=int)
with col_plan_B1:
    plan_B_live[C_ATTR_CON] = st.number_input("加点-体质 (B)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_B["point_plan"][C_ATTR_CON]), 1, key="p_con_b")
    plan_B_live[C_ATTR_STR] = st.number_input("加点-力量 (B)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_B["point_plan"][C_ATTR_STR]), 1, key="p_str_b")
    plan_B_live[C_ATTR_AGI] = st.number_input("加点-敏捷 (B)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_B["point_plan"][C_ATTR_AGI]), 1, key="p_agi_b")
with col_plan_B2:
    plan_B_live[C_ATTR_MAG] = st.number_input("加点-魔力 (B)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_B["point_plan"][C_ATTR_MAG]), 1, key="p_mag_b")
    plan_B_live[C_ATTR_ADJ] = st.number_input("加点-耐力 (B)", 0, C_LEVEL_ATTR_NUM, int(CONFIG_BEAST_B["point_plan"][C_ATTR_ADJ]), 1, key="p_adj_b")

total_points_B = np.sum(plan_B_live)
validate_data(total_points_B, C_LEVEL_ATTR_NUM,
              f"❌ 警告：B 的升级加点总数不能超过 {C_LEVEL_ATTR_NUM} 点！(当前 {total_points_B:.0f} 点)",
              f"⚠️ 提示：B 还有 {(C_LEVEL_ATTR_NUM - total_points_B):.0f} 点未分配")

# ==================== 5. 核心数学模型计算函数 ====================
levels = np.arange(0, LEVEL_NUM, 1)

# 计算面板数值
def calc_properties(growth, apt, init, plan):
    # 算全等级五维属性轴 (初始 + 天然成长1点 + 自由潜能加点)
    con_c = init[C_ATTR_CON] + levels * (1 + plan[C_ATTR_CON])
    mag_c = init[C_ATTR_MAG] + levels * (1 + plan[C_ATTR_MAG])
    str_c = init[C_ATTR_STR] + levels * (1 + plan[C_ATTR_STR])
    adj_c = init[C_ATTR_ADJ] + levels * (1 + plan[C_ATTR_ADJ])
    agi_c = init[C_ATTR_AGI] + levels * (1 + plan[C_ATTR_AGI])
    
    # 梦幻西游官方公式换算
    hpv = levels * apt[C_APT_CON] / 1000 + con_c * growth * 6
    mpv = levels * apt[C_APT_MAG] / 500 + mag_c * growth * 3
    dmg = levels * apt[C_APT_ATK] * (14 + 10 * growth) / 7500 + str_c * growth
    dfn = levels * apt[C_APT_DEF] * (9.4 + (19 / 3) * growth) / 7500 + adj_c * growth * 4 / 3
    spd = agi_c * apt[C_APT_AGI] / 1000
    mpr = levels * (apt[C_APT_MAG] + 1662) * (1 + growth) / 7500 + con_c * 0.3 + mag_c * 0.7 + str_c * 0.4 + adj_c * 0.2
    return hpv, mpv, dmg, dfn, spd, mpr

# 批量执行计算 (传入完全常量与数组化的参数)
hpv_A, mpv_A, dmg_A, dfn_A, spd_A, mpr_A = calc_properties(growth_A, apt_A, init_A, plan_A_live)
hpv_B, mpv_B, dmg_B, dfn_B, spd_B, mpr_B = calc_properties(growth_B, apt_B, init_B, plan_B_live)


# ==================== 6. 右侧主要内容区域：双曲线合并绘制 ====================
col_plot, col_data = st.columns([3, 2])

with col_plot:
    st.subheader("📈 召唤兽 A vs 召唤兽 B 属性对比图")
    fig, axs = plt.subplots(3, 2, figsize=(11, 7), dpi=100)
    
    def plot_subplot(ax, data_A, data_B, title):
        ax.plot(levels, data_A, color='#1f77b4', linewidth=2.5, label=CONFIG_BEAST_A["name"])
        ax.plot(levels, data_B, color='#d62728', linewidth=2.5, linestyle='--', label=CONFIG_BEAST_B["name"])
        ax.set_title(title)
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

    plot_subplot(axs[0, 0], hpv_A, hpv_B, "面板气血对比")
    plot_subplot(axs[0, 1], mpv_A, mpv_B, "面板魔法对比")
    plot_subplot(axs[1, 0], dmg_A, dmg_B, "面板攻击对比")
    plot_subplot(axs[1, 1], dfn_A, dfn_B, "面板防御对比")
    plot_subplot(axs[2, 0], spd_A, spd_B, "面板速度对比")
    plot_subplot(axs[2, 1], mpr_A, mpr_B, "面板法伤对比")
    
    for ax in axs.flat:
        ax.set_xlabel("等级 (Level)", fontsize=9)
    
    plt.tight_layout()
    st.pyplot(fig)

with col_data:
    st.subheader("🔍 任意等级段差值动态切片")
    
    # 【核心优化】：引入用于结算差值的等级滑动条，支持玩家最爱的核心卡级段一键拖动
    target_level = st.slider("请选择需要比对的具体等级 (Level)", min_value=0, max_value=MAX_LEVEL, value=75, step=1)
    
    # 动态在左侧对应图表上，也可以给玩家指出他们当前看的是哪一级（高级交互）
    st.markdown(f"##### 🎯 当前正在扫描：**{target_level} 级** (如：精锐69/勇武89/神威109/天科129/天元180)")
    
    # 利用滑块生成的 target_level 整数，直接去一维数组里精准索引该等级的数据点
    diff_data = {
        "属性项": ["面板气血", "面板魔法", "面板攻击", "面板防御", "面板速度", "面板法伤"],
        f"召唤兽 A ({target_level}级)": [hpv_A[target_level], mpv_A[target_level], dmg_A[target_level], dfn_A[target_level], spd_A[target_level], mpr_A[target_level]],
        f"召唤兽 B ({target_level}级)": [hpv_B[target_level], mpv_B[target_level], dmg_B[target_level], dfn_B[target_level], spd_B[target_level], mpr_B[target_level]],
        "差值 (B - A)": [
            hpv_B[target_level] - hpv_A[target_level], 
            mpv_B[target_level] - mpv_A[target_level], 
            dmg_B[target_level] - dmg_A[target_level], 
            dfn_B[target_level] - dfn_A[target_level], 
            spd_B[target_level] - spd_A[target_level],
            mpr_B[target_level] - mpr_A[target_level]
        ]
    }
    
    df_diff = pd.DataFrame(diff_data).set_index("属性项").round(1)
    st.dataframe(df_diff, use_container_width=True)
    
    # 动态提示词，根据选择的级别智能化转换
    if target_level < 69:
        st.info("💡 处于低等级阶段，资质和成长引发的乘数效应尚未完全展开，此时初始属性点的占比相对较高。")
    elif 69 <= target_level <= 129:
        st.info("💡 等级越高，成长和资质引发的乘数效应越显著。")
