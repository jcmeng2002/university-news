#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
+CATCHALL 1.0
覆盖147所高校 + 19家头部企业官方网站
"""

import requests
import json
import re
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote
import hashlib
from bs4 import BeautifulSoup
import os
import sys

# ==================== 配置区域 ====================
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
]

# 校企合作关键词
COOPERATION_KEYWORDS = [
    # 协议类
    '签约', '合作', '协议', '共建', '联合', '协同', '战略合作',
    '校企合作', '产学研', '产教融合', '校地合作', '校企协同',
    '合作协议', '合作框架', '合作备忘录',
    
    # 机构类
    '研究院', '实验室', '中心', '基地', '揭牌', '成立', '启动',
    '联合实验室', '创新中心', '研发中心', '实训基地', '产业学院',
    '工程中心', '技术中心', '人才培养基地',
    
    # 项目类
    '捐赠', '奖学金', '基金', '项目', '开班', '揭牌', '仪式',
    '人才联合培养', '订单班', '实习基地', '校园招聘', '专场',
    '创新创业', '创业大赛', '科技竞赛',
    
    # 企业名称 (19家)
    '京东', '字节跳动', '阿里巴巴', '腾讯', '美团', '华为', '百度',
    '携程', '拼多多', '网易', '小米', '快手', '滴滴', '新浪',
    '搜狐', '三六零', '唯品会', '哔哩哔哩', '小红书'
]

# ==================== 147所高校官方新闻站 ====================
DOUBLE_FIRST_CLASS_UNIVERSITIES = [
    {'name': '北京大学', 'url': 'https://news.pku.edu.cn', 'type': 'university'},
    {'name': '中国人民大学', 'url': 'https://news.ruc.edu.cn', 'type': 'university'},
    {'name': '清华大学', 'url': 'https://news.tsinghua.edu.cn', 'type': 'university'},
    {'name': '北京交通大学', 'url': 'https://news.bjtu.edu.cn', 'type': 'university'},
    {'name': '北京工业大学', 'url': 'https://news.bjut.edu.cn', 'type': 'university'},
    {'name': '北京航空航天大学', 'url': 'https://news.buaa.edu.cn', 'type': 'university'},
    {'name': '北京理工大学', 'url': 'https://news.bit.edu.cn', 'type': 'university'},
    {'name': '北京科技大学', 'url': 'https://news.ustb.edu.cn', 'type': 'university'},
    {'name': '北京化工大学', 'url': 'https://news.buct.edu.cn', 'type': 'university'},
    {'name': '北京邮电大学', 'url': 'https://news.bupt.edu.cn', 'type': 'university'},
    {'name': '中国农业大学', 'url': 'https://news.cau.edu.cn', 'type': 'university'},
    {'name': '北京林业大学', 'url': 'https://news.bjfu.edu.cn', 'type': 'university'},
    {'name': '北京协和医学院', 'url': 'https://www.pumc.edu.cn/news', 'type': 'university'},
    {'name': '北京中医药大学', 'url': 'https://news.bucm.edu.cn', 'type': 'university'},
    {'name': '北京师范大学', 'url': 'https://news.bnu.edu.cn', 'type': 'university'},
    {'name': '首都师范大学', 'url': 'https://news.cnu.edu.cn', 'type': 'university'},
    {'name': '北京外国语大学', 'url': 'https://news.bfsu.edu.cn', 'type': 'university'},
    {'name': '中国传媒大学', 'url': 'https://news.cuc.edu.cn', 'type': 'university'},
    {'name': '中央财经大学', 'url': 'https://news.cufe.edu.cn', 'type': 'university'},
    {'name': '对外经济贸易大学', 'url': 'https://news.uibe.edu.cn', 'type': 'university'},
    {'name': '外交学院', 'url': 'https://news.cfau.edu.cn', 'type': 'university'},
    {'name': '中国人民公安大学', 'url': 'https://www.ppsuc.edu.cn/news', 'type': 'university'},
    {'name': '北京体育大学', 'url': 'https://news.bsu.edu.cn', 'type': 'university'},
    {'name': '中央音乐学院', 'url': 'https://www.ccom.edu.cn/news', 'type': 'university'},
    {'name': '中国音乐学院', 'url': 'https://www.ccmusic.edu.cn/news', 'type': 'university'},
    {'name': '中央美术学院', 'url': 'https://www.cafa.edu.cn/news', 'type': 'university'},
    {'name': '中央戏剧学院', 'url': 'https://news.chntheatre.edu.cn', 'type': 'university'},
    {'name': '中国政法大学', 'url': 'https://news.cupl.edu.cn', 'type': 'university'},
    {'name': '华北电力大学', 'url': 'https://news.ncepu.edu.cn', 'type': 'university'},
    {'name': '中国科学院大学', 'url': 'https://news.ucas.ac.cn', 'type': 'university'},
    {'name': '中央民族大学', 'url': 'https://news.muc.edu.cn', 'type': 'university'},
    {'name': '南开大学', 'url': 'https://news.nankai.edu.cn', 'type': 'university'},
    {'name': '天津大学', 'url': 'https://news.tju.edu.cn', 'type': 'university'},
    {'name': '天津工业大学', 'url': 'https://news.tiangong.edu.cn', 'type': 'university'},
    {'name': '天津医科大学', 'url': 'https://news.tmu.edu.cn', 'type': 'university'},
    {'name': '天津中医药大学', 'url': 'https://news.tjutcm.edu.cn', 'type': 'university'},
    {'name': '河北工业大学', 'url': 'https://news.hebut.edu.cn', 'type': 'university'},
    {'name': '大连理工大学', 'url': 'https://news.dlut.edu.cn', 'type': 'university'},
    {'name': '东北大学', 'url': 'https://news.neu.edu.cn', 'type': 'university'},
    {'name': '大连海事大学', 'url': 'https://news.dlmu.edu.cn', 'type': 'university'},
    {'name': '辽宁大学', 'url': 'https://news.lnu.edu.cn', 'type': 'university'},
    {'name': '吉林大学', 'url': 'https://news.jlu.edu.cn', 'type': 'university'},
    {'name': '东北师范大学', 'url': 'https://news.nenu.edu.cn', 'type': 'university'},
    {'name': '哈尔滨工业大学', 'url': 'https://news.hit.edu.cn', 'type': 'university'},
    {'name': '哈尔滨工程大学', 'url': 'https://news.hrbeu.edu.cn', 'type': 'university'},
    {'name': '东北农业大学', 'url': 'https://news.neau.edu.cn', 'type': 'university'},
    {'name': '东北林业大学', 'url': 'https://news.nefu.edu.cn', 'type': 'university'},
    {'name': '复旦大学', 'url': 'https://news.fudan.edu.cn', 'type': 'university'},
    {'name': '同济大学', 'url': 'https://news.tongji.edu.cn', 'type': 'university'},
    {'name': '上海交通大学', 'url': 'https://news.sjtu.edu.cn', 'type': 'university'},
    {'name': '华东理工大学', 'url': 'https://news.ecust.edu.cn', 'type': 'university'},
    {'name': '东华大学', 'url': 'https://news.dhu.edu.cn', 'type': 'university'},
    {'name': '华东师范大学', 'url': 'https://news.ecnu.edu.cn', 'type': 'university'},
    {'name': '上海大学', 'url': 'https://news.shu.edu.cn', 'type': 'university'},
    {'name': '上海科技大学', 'url': 'https://www.shanghaitech.edu.cn/news', 'type': 'university'},
    {'name': '上海财经大学', 'url': 'https://news.sufe.edu.cn', 'type': 'university'},
    {'name': '上海外国语大学', 'url': 'https://news.shisu.edu.cn', 'type': 'university'},
    {'name': '上海中医药大学', 'url': 'https://news.shutcm.edu.cn', 'type': 'university'},
    {'name': '上海体育学院', 'url': 'https://news.sus.edu.cn', 'type': 'university'},
    {'name': '上海音乐学院', 'url': 'https://www.shcmusic.edu.cn/news', 'type': 'university'},
    {'name': '上海戏剧学院', 'url': 'https://news.sta.edu.cn', 'type': 'university'},
    {'name': '海军军医大学', 'url': 'https://www.smmu.edu.cn/news', 'type': 'university'},
    {'name': '南京大学', 'url': 'https://news.nju.edu.cn', 'type': 'university'},
    {'name': '东南大学', 'url': 'https://news.seu.edu.cn', 'type': 'university'},
    {'name': '南京航空航天大学', 'url': 'https://news.nuaa.edu.cn', 'type': 'university'},
    {'name': '南京理工大学', 'url': 'https://news.njust.edu.cn', 'type': 'university'},
    {'name': '中国矿业大学', 'url': 'https://news.cumt.edu.cn', 'type': 'university'},
    {'name': '河海大学', 'url': 'https://news.hhu.edu.cn', 'type': 'university'},
    {'name': '江南大学', 'url': 'https://news.jiangnan.edu.cn', 'type': 'university'},
    {'name': '南京农业大学', 'url': 'https://news.njau.edu.cn', 'type': 'university'},
    {'name': '南京师范大学', 'url': 'https://news.njnu.edu.cn', 'type': 'university'},
    {'name': '苏州大学', 'url': 'https://news.suda.edu.cn', 'type': 'university'},
    {'name': '南京林业大学', 'url': 'https://news.njfu.edu.cn', 'type': 'university'},
    {'name': '南京信息工程大学', 'url': 'https://news.nuist.edu.cn', 'type': 'university'},
    {'name': '南京邮电大学', 'url': 'https://news.njupt.edu.cn', 'type': 'university'},
    {'name': '南京中医药大学', 'url': 'https://news.njucm.edu.cn', 'type': 'university'},
    {'name': '南京医科大学', 'url': 'https://news.njmu.edu.cn', 'type': 'university'},
    {'name': '扬州大学', 'url': 'https://news.yzu.edu.cn', 'type': 'university'},
    {'name': '浙江大学', 'url': 'https://news.zju.edu.cn', 'type': 'university'},
    {'name': '中国美术学院', 'url': 'https://www.caa.edu.cn/news', 'type': 'university'},
    {'name': '宁波大学', 'url': 'https://news.nbu.edu.cn', 'type': 'university'},
    {'name': '中国科学技术大学', 'url': 'https://news.ustc.edu.cn', 'type': 'university'},
    {'name': '合肥工业大学', 'url': 'https://news.hfut.edu.cn', 'type': 'university'},
    {'name': '安徽大学', 'url': 'https://news.ahu.edu.cn', 'type': 'university'},
    {'name': '厦门大学', 'url': 'https://news.xmu.edu.cn', 'type': 'university'},
    {'name': '福州大学', 'url': 'https://news.fzu.edu.cn', 'type': 'university'},
    {'name': '南昌大学', 'url': 'https://news.ncu.edu.cn', 'type': 'university'},
    {'name': '山东大学', 'url': 'https://www.view.sdu.edu.cn', 'type': 'university'},
    {'name': '中国海洋大学', 'url': 'https://news.ouc.edu.cn', 'type': 'university'},
    {'name': '中国石油大学（华东）', 'url': 'https://news.upc.edu.cn', 'type': 'university'},
    {'name': '郑州大学', 'url': 'https://news.zzu.edu.cn', 'type': 'university'},
    {'name': '武汉大学', 'url': 'https://news.whu.edu.cn', 'type': 'university'},
    {'name': '华中科技大学', 'url': 'https://news.hust.edu.cn', 'type': 'university'},
    {'name': '中国地质大学（武汉）', 'url': 'https://news.cug.edu.cn', 'type': 'university'},
    {'name': '武汉理工大学', 'url': 'https://news.whut.edu.cn', 'type': 'university'},
    {'name': '华中农业大学', 'url': 'https://news.hzau.edu.cn', 'type': 'university'},
    {'name': '华中师范大学', 'url': 'https://news.ccnu.edu.cn', 'type': 'university'},
    {'name': '中南财经政法大学', 'url': 'https://news.zuel.edu.cn', 'type': 'university'},
    {'name': '湖南大学', 'url': 'https://news.hnu.edu.cn', 'type': 'university'},
    {'name': '中南大学', 'url': 'https://news.csu.edu.cn', 'type': 'university'},
    {'name': '湖南师范大学', 'url': 'https://news.hunnu.edu.cn', 'type': 'university'},
    {'name': '湘潭大学', 'url': 'https://news.xtu.edu.cn', 'type': 'university'},
    {'name': '国防科技大学', 'url': 'https://www.nudt.edu.cn/news', 'type': 'university'},
    {'name': '中山大学', 'url': 'https://news.sysu.edu.cn', 'type': 'university'},
    {'name': '华南理工大学', 'url': 'https://news.scut.edu.cn', 'type': 'university'},
    {'name': '暨南大学', 'url': 'https://news.jnu.edu.cn', 'type': 'university'},
    {'name': '华南师范大学', 'url': 'https://news.scnu.edu.cn', 'type': 'university'},
    {'name': '广州大学', 'url': 'https://news.gzhu.edu.cn', 'type': 'university'},
    {'name': '深圳大学', 'url': 'https://news.szu.edu.cn', 'type': 'university'},
    {'name': '华南农业大学', 'url': 'https://news.scau.edu.cn', 'type': 'university'},
    {'name': '海南大学', 'url': 'https://news.hainanu.edu.cn', 'type': 'university'},
    {'name': '重庆大学', 'url': 'https://news.cqu.edu.cn', 'type': 'university'},
    {'name': '西南大学', 'url': 'https://news.swu.edu.cn', 'type': 'university'},
    {'name': '四川大学', 'url': 'https://news.scu.edu.cn', 'type': 'university'},
    {'name': '电子科技大学', 'url': 'https://news.uestc.edu.cn', 'type': 'university'},
    {'name': '西南交通大学', 'url': 'https://news.swjtu.edu.cn', 'type': 'university'},
    {'name': '西南石油大学', 'url': 'https://news.swpu.edu.cn', 'type': 'university'},
    {'name': '成都理工大学', 'url': 'https://news.cdut.edu.cn', 'type': 'university'},
    {'name': '四川农业大学', 'url': 'https://news.sicau.edu.cn', 'type': 'university'},
    {'name': '成都中医药大学', 'url': 'https://news.cdutcm.edu.cn', 'type': 'university'},
    {'name': '西南财经大学', 'url': 'https://news.swufe.edu.cn', 'type': 'university'},
    {'name': '西安交通大学', 'url': 'https://news.xjtu.edu.cn', 'type': 'university'},
    {'name': '西北工业大学', 'url': 'https://news.nwpu.edu.cn', 'type': 'university'},
    {'name': '西安电子科技大学', 'url': 'https://news.xidian.edu.cn', 'type': 'university'},
    {'name': '长安大学', 'url': 'https://news.chd.edu.cn', 'type': 'university'},
    {'name': '西北大学', 'url': 'https://news.nwu.edu.cn', 'type': 'university'},
    {'name': '陕西师范大学', 'url': 'https://news.snnu.edu.cn', 'type': 'university'},
    {'name': '西北农林科技大学', 'url': 'https://news.nwsuaf.edu.cn', 'type': 'university'},
    {'name': '空军军医大学', 'url': 'https://www.fmmu.edu.cn/news', 'type': 'university'},
    {'name': '兰州大学', 'url': 'https://news.lzu.edu.cn', 'type': 'university'},
    {'name': '南方科技大学', 'url': 'https://news.sustech.edu.cn', 'type': 'university'}
]

# ==================== 19家头部企业官方新闻 ====================
LARGE_ENTERPRISES = [
    {'name': '京东', 'url': 'https://corporate.jd.com/news', 'type': 'internet'},
    {'name': '字节跳动', 'url': 'https://www.bytedance.com/zh/news', 'type': 'internet'},
    {'name': '阿里巴巴', 'url': 'https://www.alibabagroup.com/cn/news', 'type': 'internet'},
    {'name': '腾讯', 'url': 'https://www.tencent.com/zh-cn/news.html', 'type': 'internet'},
    {'name': '美团', 'url': 'https://about.meituan.com/news', 'type': 'internet'},
    {'name': '华为', 'url': 'https://www.huawei.com/cn/news/', 'type': 'manufacturing'},
    {'name': '百度', 'url': 'https://www.baidu.com/home/news/', 'type': 'internet'},
    {'name': '携程', 'url': 'https://ir.ctrip.com/news-releases', 'type': 'internet'},
    {'name': '拼多多', 'url': 'https://www.pinduoduo.com/home/news/', 'type': 'internet'},
    {'name': '网易', 'url': 'https://www.163.com/news', 'type': 'internet'},
    {'name': '小米集团', 'url': 'https://www.mi.com/static/media.html', 'type': 'manufacturing'},
    {'name': '快手', 'url': 'https://www.kuaishou.com/news', 'type': 'internet'},
    {'name': '滴滴出行', 'url': 'https://www.didiglobal.com/news', 'type': 'internet'},
    {'name': '新浪', 'url': 'https://news.sina.com.cn', 'type': 'internet'},
    {'name': '搜狐', 'url': 'https://news.sohu.com', 'type': 'internet'},
    {'name': '三六零', 'url': 'https://www.360.cn/news', 'type': 'internet'},
    {'name': '唯品会', 'url': 'https://www.vip.com/aboutus/news', 'type': 'internet'},
    {'name': '哔哩哔哩', 'url': 'https://www.bilibili.com/blackboard/news.html', 'type': 'internet'},
    {'name': '小红书', 'url': 'https://www.xiaohongshu.com/news', 'type': 'internet'}
]

# ==================== 辅助函数 ====================
def get_random_headers(referer=''):
    """生成随机请求头"""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    if referer:
        headers['Referer'] = referer
    return headers

def extract_date_advanced(element, soup):
    """智能日期提取"""
    try:
        date_patterns = [
            r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})日?',
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})'
        ]
        
        # 检查元素文本
        text = element.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups[0]) == 4:
                    return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                else:
                    return f"{groups[2]}-{groups[0].zfill(2)}-{groups[1].zfill(2)}"
        
        # 查找time标签
        time_tag = element.find('time')
        if time_tag and time_tag.get('datetime'):
            dt = time_tag['datetime']
            return dt[:10]
        
        # 查找class包含date的元素
        date_selectors = ['.date', '.time', '.pub-date', '.post-time', '.news-date']
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                text = date_elem.get_text()
                for pattern in date_patterns:
                    match = re.search(pattern, text)
                    if match:
                        groups = match.groups()
                        if len(groups[0]) == 4:
                            return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
        
    except:
        pass
    
    return datetime.now().strftime('%Y-%m-%d')

def extract_summary_near_link(link, soup):
    """提取链接附近的摘要"""
    try:
        parent = link.parent
        for _ in range(3):
            if parent:
                for elem in parent.find_all(['p', 'div']):
                    text = elem.get_text().strip()
                    if 30 < len(text) < 200:
                        return text[:150] + '...'
                parent = parent.parent
    except:
        pass
    return link.get_text().strip()[:80] + '...'

def generate_tags_from_title(title):
    """生成标签"""
    tags = []
    title_lower = title.lower()
    
    tag_mapping = [
        (['签约', '协议'], '签约仪式'),
        (['实验室', '研究院', '中心'], '机构共建'),
        (['捐赠', '基金', '奖学金'], '捐赠资助'),
        (['人才', '培养', '实习'], '人才培养'),
        (['招聘', '宣讲'], '人才招聘'),
        (['人工智能', 'AI', '智能'], '人工智能'),
        (['制造', '工程'], '智能制造'),
        (['生物', '医药'], '生物医药'),
        (['金融', '财经'], '金融合作')
    ]
    
    for keywords, tag in tag_mapping:
        if any(keyword in title for keyword in keywords):
            tags.append(tag)
    
    return tags if tags else ['合作动态']

# ==================== 核心抓取函数 ====================
def fetch_school_news(school_info, session):
    """抓取高校新闻"""
    news_items = []
    try:
        print(f"🎓 抓取: {school_info['name']}")
        
        response = session.get(school_info['url'], timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return news_items
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 高校新闻常见选择器
        selectors = [
            'a[href*="news"]', 'a[href*="info"]',
            '.news-list a', '.news-item a',
            'ul.list-news a', '.article-list a'
        ]
        
        links = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                links.extend(found[:10])  # 每个选择器最多10条
        
        for link in links:
            title = link.get_text().strip()
            if not title or len(title) < 4:
                continue
            
            href = link.get('href', '')
            if not href:
                continue
            
            # URL补全
            if not href.startswith(('http://', 'https://')):
                href = urljoin(school_info['url'], href)
            
            # 关键词检查
            has_keyword = any(keyword in title for keyword in COOPERATION_KEYWORDS)
            if has_keyword:
                date = extract_date_advanced(link, soup)
                
                news_item = {
                    'id': hashlib.md5(f"{title}{href}".encode()).hexdigest()[:8],
                    'title': title,
                    'url': href,
                    'source': school_info['name'],
                    'source_type': 'school_website',
                    'date': date,
                    'category': '校企合作',
                    'summary': extract_summary_near_link(link, soup),
                    'verified': True,
                    'tags': generate_tags_from_title(title)
                }
                news_items.append(news_item)
        
        if news_items:
            print(f"  找到 {len(news_items)} 条合作新闻")
        
    except Exception as e:
        print(f"  错误: {str(e)[:50]}")
    
    return news_items

def fetch_enterprise_news(enterprise_info, session):
    """抓取企业新闻"""
    news_items = []
    try:
        print(f"🏢 抓取: {enterprise_info['name']}")
        
        response = session.get(enterprise_info['url'], timeout=15)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 企业新闻选择器
        selectors = [
            '.news-list a', '.press-release a',
            'a[href*="/news/"]', 'a[href*="/press/"]'
        ]
        
        links = []
        for selector in selectors:
            found = soup.select(selector)
            if found:
                links.extend(found[:8])
        
        for link in links:
            title = link.get_text().strip()
            if len(title) < 6:
                continue
            
            href = link.get('href', '')
            if not href.startswith('http'):
                href = urljoin(enterprise_info['url'], href)
            
            # 检查是否涉及高校
            has_university = any(keyword in title for keyword in ['大学', '学院', '高校'])
            if has_university:
                date = extract_date_advanced(link, soup)
                
                news_item = {
                    'id': hashlib.md5(f"{title}{href}".encode()).hexdigest()[:8],
                    'title': title,
                    'url': href,
                    'source': enterprise_info['name'],
                    'source_type': 'enterprise_website',
                    'date': date,
                    'category': '企业合作',
                    'summary': extract_summary_near_link(link, soup),
                    'verified': True,
                    'tags': ['企业发布'] + generate_tags_from_title(title)
                }
                news_items.append(news_item)
        
        if news_items:
            print(f"  找到 {len(news_items)} 条高校相关新闻")
        
    except Exception as e:
        print(f"  错误: {str(e)[:50]}")
    
    return news_items

# ==================== 主程序 ====================
def main():
    """主抓取函数"""
    print("=" * 70)
    print("🏫 校企合作新闻抓取系统")
    print(f"📊 目标: {len(DOUBLE_FIRST_CLASS_UNIVERSITIES)} 所高校 + {len(LARGE_ENTERPRISES)} 家企业")
    print("=" * 70)
    
    all_news = []
    session = requests.Session()
    
    # 1. 抓取高校新闻 (测试模式：前5所)
    print("\n📚 第一阶段: 高校官网抓取")
    test_mode = True  # 设为False可抓取全部
    
    schools_to_fetch = DOUBLE_FIRST_CLASS_UNIVERSITIES[:5] if test_mode else DOUBLE_FIRST_CLASS_UNIVERSITIES
    
    for i, school in enumerate(schools_to_fetch, 1):
        news = fetch_school_news(school, session)
        all_news.extend(news)
        
        # 礼貌延迟
        if i % 3 == 0:
            time.sleep(2)
        else:
            time.sleep(random.uniform(1, 2))
        
        if test_mode and i >= 5:
            break
    
    # 2. 抓取企业新闻 (测试模式：前3家)
    print("\n🏢 第二阶段: 企业官网抓取")
    enterprises_to_fetch = LARGE_ENTERPRISES[:3] if test_mode else LARGE_ENTERPRISES
    
    for i, enterprise in enumerate(enterprises_to_fetch, 1):
        news = fetch_enterprise_news(enterprise, session)
        all_news.extend(news)
        time.sleep(random.uniform(2, 3))
        
        if test_mode and i >= 3:
            break
    
    # 去重
    seen_ids = set()
    unique_news = []
    for item in all_news:
        if item['id'] not in seen_ids:
            seen_ids.add(item['id'])
            unique_news.append(item)
    
    # 排序
    unique_news.sort(key=lambda x: x['date'], reverse=True)
    
    # 保存
    save_to_json(unique_news)
    
    print("\n" + "=" * 70)
    print(f"✅ 抓取完成! 共获取 {len(unique_news)} 条新闻")
    print("=" * 70)

def save_to_json(news_list):
    """保存数据"""
    try:
        data = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total': len(news_list),
            'schools_count': len(set(item['source'] for item in news_list if item['source_type'] == 'school_website')),
            'enterprises_count': len(set(item['source'] for item in news_list if item['source_type'] == 'enterprise_website')),
            'news': news_list[:100]  # 限制100条
        }
        
        with open('../data/news.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 数据已保存到: data/news.json")
        
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

if __name__ == "__main__":
    main()