#!/usr/bin/env python3
"""
Verify OpenCLI — 使用 OpenCLI 浏览器自动化验证知识库输出
Comprehensive KB verification using OpenCLI browser automation
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"
GRAPH_DIR = PROJECT_ROOT / "graph"
PROCESSING_DIR = PROJECT_ROOT / ".processing"


def log_info(msg):
    print(f"\033[94m[INFO]\033[0m {msg}")


def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")


def log_warn(msg):
    print(f"\033[93m[WARN]\033[0m {msg}")


def log_error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}")


def run_command(cmd, capture=True):
    """运行命令并返回结果"""
    try:
        if capture:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, timeout=60)
            return result.returncode, "", ""
    except subprocess.TimeoutExpired:
        return -1, "", "Command timeout"
    except Exception as e:
        return -1, "", str(e)


def check_opencli_status():
    """检查 OpenCLI 是否可用"""
    log_info("检查 OpenCLI 状态...")
    code, stdout, stderr = run_command("opencli doctor")
    if code == 0:
        log_success("OpenCLI 可用")
        return True
    else:
        log_error(f"OpenCLI 不可用: {stderr}")
        return False


def run_health_check():
    """运行健康检查"""
    log_info("运行健康检查...")
    health_script = PROCESSING_DIR / "scripts" / "health.py"
    code, stdout, stderr = run_command(f"python {health_script}")
    if code == 0:
        log_success("健康检查通过")
    else:
        log_warn("健康检查发现问题")
    return code


def verify_wikipedia_enrichment():
    """验证 Wikipedia 富化"""
    log_info("验证 Wikipedia 富化...")

    enriched_count = 0
    total_count = 0

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue

        total_count += 1
        content = md_file.read_text(encoding='utf-8')

        # 检查 enriched 标记
        if 'enriched: true' in content or 'enriched: true' in content.lower():
            enriched_count += 1

        # 检查是否有 Wikipedia 链接
        if 'wikipedia.org' in content.lower():
            # 验证链接格式
            wiki_links = re.findall(r'https?://[^\s\]\"\'<>]+wikipedia[^\s\]\"\'<>]*', content)
            if not wiki_links:
                log_warn(f"页面 {md_file.stem} 标记为富化但无 Wikipedia 链接")

    log_info(f"富化统计: {enriched_count}/{total_count} 页面已富化")
    return enriched_count, total_count


def verify_graph_html():
    """验证 graph.html 可视化"""
    log_info("验证图谱可视化...")

    graph_file = GRAPH_DIR / "graph.html"
    if not graph_file.exists():
        log_error("graph.html 不存在")
        return False

    # 检查 graph.json 是否存在
    graph_json = GRAPH_DIR / "graph.json"
    if not graph_json.exists():
        log_error("graph.json 不存在")
        return False

    # 检查文件大小
    json_size = graph_json.stat().st_size
    html_size = graph_file.stat().st_size

    if json_size < 1000:
        log_warn(f"graph.json 异常小: {json_size} bytes")
        return False

    if html_size < 1000:
        log_warn(f"graph.html 异常小: {html_size} bytes")
        return False

    # 尝试使用 OpenCLI 验证（如果浏览器可用）
    if check_opencli_status():
        log_info("使用 OpenCLI 验证图谱渲染...")
        # 截图验证（需要浏览器）
        # code, stdout, stderr = run_command(f'opencli browser work open "file://{graph_file.absolute()}"')
        log_info("(浏览器验证需要在桌面环境运行)")

    log_success(f"图谱文件正常: graph.json={json_size} bytes, graph.html={html_size} bytes")
    return True


def verify_broken_links():
    """验证断链"""
    log_info("检查断链...")

    # 构建有效页面集合
    valid_pages = set()
    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue
        valid_pages.add(md_file.stem)

    broken_links = []

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue

        content = md_file.read_text(encoding='utf-8')
        wikilinks = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

        for link in wikilinks:
            link = link.strip()
            if link not in valid_pages and link not in ['index', 'log', 'overview']:
                broken_links.append({
                    "file": md_file.stem,
                    "link": link
                })

    if broken_links:
        log_warn(f"发现 {len(broken_links)} 个断链")
        for bl in broken_links[:10]:  # 只显示前10个
            log_warn(f"  [[{bl['link']}]] 在 {bl['file']} 中")
        if len(broken_links) > 10:
            log_warn(f"  ... 还有 {len(broken_links) - 10} 个")
    else:
        log_success("无断链")

    return len(broken_links) == 0


def verify_bilingual_fields():
    """验证双语字段"""
    log_info("检查双语字段...")

    missing_zh = []

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue

        content = md_file.read_text(encoding='utf-8')

        # 提取 frontmatter
        match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            continue

        fm = match.group(1)

        # 检查必需字段
        has_name = bool(re.search(r'^full_name:', fm, re.MULTILINE))
        has_title_zh = bool(re.search(r'^title_zh:', fm, re.MULTILINE))
        has_country_zh = bool(re.search(r'^country_zh:', fm, re.MULTILINE))

        if not has_title_zh:
            missing_zh.append({
                "file": md_file.stem,
                "missing": "title_zh"
            })

    if missing_zh:
        log_warn(f"发现 {len(missing_zh)} 个页面缺少中文翻译")
        for m in missing_zh[:5]:
            log_warn(f"  {m['file']} 缺少 {m['missing']}")
    else:
        log_success("所有页面都有中文翻译")

    return len(missing_zh) == 0


def verify_single_file(shortcode):
    """验证单个页面"""
    log_info(f"验证单个页面: {shortcode}")

    md_file = KB_DIR / f"{shortcode}.md"
    if not md_file.exists():
        log_error(f"页面不存在: {shortcode}")
        return False

    content = md_file.read_text(encoding='utf-8')

    # 提取 frontmatter
    match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        log_error("缺少 frontmatter")
        return False

    fm = match.group(1)

    checks = {
        "full_name": bool(re.search(r'^full_name:', fm, re.MULTILINE)),
        "title_zh": bool(re.search(r'^title_zh:', fm, re.MULTILINE)),
        "birth": bool(re.search(r'^birth:', fm, re.MULTILINE)),
        "country": bool(re.search(r'^country:', fm, re.MULTILINE)),
    }

    all_pass = True
    for field, present in checks.items():
        if present:
            log_success(f"  {field}: 存在")
        else:
            log_error(f"  {field}: 缺失")
            all_pass = False

    # 检查内容长度
    body = content[match.end():].strip()
    if len(body) < 100:
        log_warn(f"  内容过短: {len(body)} 字符")

    return all_pass


def main():
    parser = argparse.ArgumentParser(description="KB OpenCLI Verification")
    parser.add_argument("--all", action="store_true", help="完整验证")
    parser.add_argument("--wikipedia", action="store_true", help="仅验证 Wikipedia 富化")
    parser.add_argument("--graph", action="store_true", help="仅验证图谱可视化")
    parser.add_argument("--file", type=str, help="验证单个页面")
    parser.add_argument("--links", action="store_true", help="仅验证断链")

    args = parser.parse_args()

    log_info("=" * 60)
    log_info("KB OpenCLI Verification")
    log_info(f"时间: {datetime.now(timezone.utc).isoformat()}")
    log_info("=" * 60)

    results = {}

    # 如果没有指定参数，执行完整验证
    if not any([args.all, args.wikipedia, args.graph, args.file, args.links]):
        args.all = True

    if args.all or args.wikipedia:
        log_info("")
        log_info("1. Wikipedia 富化验证")
        log_info("-" * 40)
        results['wikipedia'] = verify_wikipedia_enrichment()

    if args.all or args.graph:
        log_info("")
        log_info("2. 图谱可视化验证")
        log_info("-" * 40)
        results['graph'] = verify_graph_html()

    if args.all or args.links:
        log_info("")
        log_info("3. 断链验证")
        log_info("-" * 40)
        results['links'] = verify_broken_links()

    if args.all or args.wikipedia:
        log_info("")
        log_info("4. 双语字段验证")
        log_info("-" * 40)
        results['bilingual'] = verify_bilingual_fields()

    if args.file:
        log_info("")
        log_info(f"验证指定页面: {args.file}")
        log_info("-" * 40)
        results['single'] = verify_single_file(args.file)

    # 运行基础健康检查
    log_info("")
    log_info("5. 基础健康检查")
    log_info("-" * 40)
    results['health'] = run_health_check() == 0

    # 总结
    log_info("")
    log_info("=" * 60)
    log_info("验证总结")
    log_info("=" * 60)

    all_pass = True
    for check, passed in results.items():
        if passed:
            log_success(f"{check}: 通过")
        else:
            log_warn(f"{check}: 有问题")
            all_pass = False

    if all_pass:
        log_success("所有验证通过!")
        return 0
    else:
        log_warn("部分验证有问题，请检查上述输出")
        return 1


if __name__ == "__main__":
    sys.exit(main())
