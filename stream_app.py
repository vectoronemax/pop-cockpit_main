"""Streamlit 入口：streamlit run stream_app.py。"""
from pathlib import Path
import re

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent


def build_dashboard_html(base_dir: Path = BASE_DIR) -> str:
    """将仓库内的 JS 内联，避免 iframe 无法访问相对路径。"""
    html = (base_dir / 'index.html').read_text(encoding='utf-8')
    sources = {
        './data.js': base_dir / 'data.js',
        './assets/china.js': base_dir / 'assets/china.js',
        './assets/echarts.min.js': base_dir / 'assets/echarts.min.js',
    }
    for src, path in sources.items():
        tag = f'<script src="{src}"></script>'
        if html.count(tag) != 1:
            raise ValueError(f'页面脚本引用发生变化：{src}')
        javascript = path.read_text(encoding='utf-8')
        # 防止脚本内容中的结束标签提前关闭 HTML script 元素。
        javascript = re.sub(r'</script', lambda _: r'<\/script', javascript, flags=re.IGNORECASE)
        html = html.replace(tag, '<script>\n' + javascript + '\n</script>')
    return html


def main() -> None:
    st.set_page_config(page_title='中国人口版图驾驶舱', page_icon='📊', layout='wide')
    st.markdown(
        '<style>.stApp {background:#030915;} '
        '.block-container {padding-top:1rem;padding-bottom:1rem;}</style>',
        unsafe_allow_html=True,
    )
    with st.expander('浏览设置与数据说明', expanded=False):
        height = st.slider('大屏显示高度（像素）', 500, 1200, 850, 50)
        st.caption('手机竖屏可在大屏区域内滚动浏览；横屏查看更方便。')
        st.caption('数据来源：中国人口和就业统计年鉴 2024、七普；'
                   '底图：DataV.GeoAtlas（高德），仅用于教学与学习交流。详细口径见仓库 README。')
    try:
        html = build_dashboard_html()
    except (OSError, ValueError) as exc:
        st.error(f'大屏文件加载失败：{exc}')
        st.info('请确认 index.html、data.js 和 assets/ 与 stream_app.py 一起上传。')
        st.stop()
    # 新版 Streamlit 使用 st.iframe；兼容仍使用 components 的旧版。
    if hasattr(st, 'iframe'):
        st.iframe(html, height=height)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=height, scrolling=True)


if __name__ == '__main__':
    main()
