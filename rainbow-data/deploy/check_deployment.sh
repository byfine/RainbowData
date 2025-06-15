#!/bin/bash
# 彩虹数据 (RainbowData) 部署状态检查脚本
# 用途：验证生产环境部署是否成功，检查各项服务状态
# 版本：v1.0
# 创建时间：2025年6月

set -e  # 遇到错误立即退出

echo "🔍 开始检查彩虹数据部署状态..."

# 配置变量
PROJECT_DIR="/var/www/rainbow-data"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="/var/log/rainbow-data"

# 颜色输出定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 状态计数器
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 检查结果函数
check_result() {
    local status=$1
    local message=$2
    local type=${3:-"info"}
    
    if [ "$status" = "0" ]; then
        echo -e "✅ ${GREEN}PASS${NC} - $message"
        ((PASS_COUNT++))
    elif [ "$type" = "warning" ]; then
        echo -e "⚠️  ${YELLOW}WARN${NC} - $message"
        ((WARN_COUNT++))
    else
        echo -e "❌ ${RED}FAIL${NC} - $message"
        ((FAIL_COUNT++))
    fi
}

echo ""
echo "🔧 1. 系统基础服务检查"
echo "================================"

# 检查系统服务
services=("nginx" "mysql" "redis-server")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        check_result 0 "$service 服务运行正常"
    else
        check_result 1 "$service 服务未运行"
    fi
done

echo ""
echo "🐍 2. Python环境检查"
echo "================================"

# 检查Python虚拟环境
if [ -d "$BACKEND_DIR/venv" ]; then
    check_result 0 "Python虚拟环境存在"
    
    # 检查虚拟环境中的Python版本
    if [ -f "$BACKEND_DIR/venv/bin/python" ]; then
        PYTHON_VERSION=$("$BACKEND_DIR/venv/bin/python" --version 2>&1)
        check_result 0 "Python版本: $PYTHON_VERSION"
    else
        check_result 1 "虚拟环境中的Python不存在"
    fi
else
    check_result 1 "Python虚拟环境不存在"
fi

# 检查Django应用
if [ -f "$BACKEND_DIR/manage.py" ]; then
    check_result 0 "Django应用文件存在"
    
    # 检查Django配置
    cd "$BACKEND_DIR"
    if source venv/bin/activate && python manage.py check --deploy --settings=rainbow_data.settings.production 2>/dev/null; then
        check_result 0 "Django配置检查通过"
    else
        check_result 1 "Django配置检查失败" "warning"
    fi
else
    check_result 1 "Django应用文件不存在"
fi

echo ""
echo "🚀 3. 应用服务检查"
echo "================================"

# 检查Gunicorn服务
if systemctl is-active --quiet "rainbow-data-gunicorn"; then
    check_result 0 "Gunicorn服务运行正常"
    
    # 检查Gunicorn进程
    GUNICORN_PROCESSES=$(pgrep -f "gunicorn.*rainbow_data" | wc -l)
    if [ "$GUNICORN_PROCESSES" -gt 0 ]; then
        check_result 0 "Gunicorn worker进程: $GUNICORN_PROCESSES 个"
    else
        check_result 1 "未发现Gunicorn worker进程"
    fi
else
    check_result 1 "Gunicorn服务未运行"
fi

# 检查端口监听
if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    check_result 0 "Django应用端口8000监听正常"
else
    check_result 1 "Django应用端口8000未监听"
fi

echo ""
echo "🌐 4. Web服务检查"
echo "================================"

# 检查Nginx配置
if nginx -t 2>/dev/null; then
    check_result 0 "Nginx配置文件语法正确"
else
    check_result 1 "Nginx配置文件语法错误"
fi

# 检查Nginx站点配置
if [ -f "/etc/nginx/sites-enabled/rainbow-data" ]; then
    check_result 0 "Nginx站点配置已启用"
else
    check_result 1 "Nginx站点配置未启用"
fi

# 检查端口监听
if netstat -tlnp 2>/dev/null | grep -q ":80"; then
    check_result 0 "Nginx HTTP端口80监听正常"
else
    check_result 1 "Nginx HTTP端口80未监听"
fi

if netstat -tlnp 2>/dev/null | grep -q ":443"; then
    check_result 0 "Nginx HTTPS端口443监听正常"
else
    check_result 0 "Nginx HTTPS端口443未配置" "warning"
fi

echo ""
echo "📁 5. 文件和目录检查"
echo "================================"

# 检查项目目录
directories=("$PROJECT_DIR" "$BACKEND_DIR" "$FRONTEND_DIR" "$LOG_DIR")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        check_result 0 "目录存在: $dir"
    else
        check_result 1 "目录不存在: $dir"
    fi
done

# 检查静态文件
if [ -d "$BACKEND_DIR/static" ] && [ "$(ls -A "$BACKEND_DIR/static" 2>/dev/null)" ]; then
    check_result 0 "Django静态文件已收集"
else
    check_result 1 "Django静态文件未收集"
fi

# 检查前端文件
if [ -f "$FRONTEND_DIR/index.html" ]; then
    check_result 0 "前端主页文件存在"
else
    check_result 1 "前端主页文件不存在"
fi

echo ""
echo "🗄️  6. 数据库连接检查"
echo "================================"

# 检查MySQL连接
if mysql -u root -e "SELECT 1;" 2>/dev/null; then
    check_result 0 "MySQL数据库连接正常"
    
    # 检查应用数据库
    if mysql -u root -e "USE rainbow_data_prod; SELECT 1;" 2>/dev/null; then
        check_result 0 "应用数据库rainbow_data_prod存在"
    else
        check_result 1 "应用数据库rainbow_data_prod不存在"
    fi
else
    check_result 1 "MySQL数据库连接失败"
fi

# 检查Redis连接
if redis-cli ping 2>/dev/null | grep -q "PONG"; then
    check_result 0 "Redis缓存服务连接正常"
else
    check_result 1 "Redis缓存服务连接失败"
fi

echo ""
echo "📊 7. HTTP服务检查"
echo "================================"

# 检查HTTP响应
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    check_result 0 "HTTP主页访问正常 (状态码: $HTTP_CODE)"
elif [ "$HTTP_CODE" = "000" ]; then
    check_result 1 "HTTP服务无法访问"
else
    check_result 1 "HTTP访问异常 (状态码: $HTTP_CODE)" "warning"
fi

# 检查API接口
API_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/results/ 2>/dev/null || echo "000")
if [ "$API_CODE" = "200" ]; then
    check_result 0 "API接口访问正常 (状态码: $API_CODE)"
elif [ "$API_CODE" = "000" ]; then
    check_result 1 "API接口无法访问"
else
    check_result 1 "API接口访问异常 (状态码: $API_CODE)" "warning"
fi

echo ""
echo "📝 8. 日志文件检查"
echo "================================"

# 检查日志文件
log_files=(
    "$LOG_DIR/nginx_access.log"
    "$LOG_DIR/nginx_error.log"
    "$LOG_DIR/django.log"
)

for log_file in "${log_files[@]}"; do
    if [ -f "$log_file" ]; then
        check_result 0 "日志文件存在: $(basename "$log_file")"
    else
        check_result 1 "日志文件不存在: $(basename "$log_file")" "warning"
    fi
done

# 检查最近的错误日志
ERROR_COUNT=$(tail -n 100 "$LOG_DIR/nginx_error.log" 2>/dev/null | grep -i error | wc -l || echo "0")
if [ "$ERROR_COUNT" -eq 0 ]; then
    check_result 0 "最近无Nginx错误日志"
else
    check_result 1 "最近有 $ERROR_COUNT 条Nginx错误日志" "warning"
fi

echo ""
echo "🔒 9. 安全配置检查"
echo "================================"

# 检查防火墙状态
if ufw status | grep -q "Status: active"; then
    check_result 0 "UFW防火墙已启用"
else
    check_result 1 "UFW防火墙未启用" "warning"
fi

# 检查文件权限
if [ "$(stat -c '%U' "$PROJECT_DIR")" = "rainbowdata" ]; then
    check_result 0 "项目目录所有者正确"
else
    check_result 1 "项目目录所有者不正确"
fi

echo ""
echo "📈 10. 性能状态检查"
echo "================================"

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_result 0 "磁盘使用率正常 ($DISK_USAGE%)"
else
    check_result 1 "磁盘使用率过高 ($DISK_USAGE%)" "warning"
fi

# 检查内存使用
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
check_result 0 "内存使用率: ${MEMORY_USAGE}%"

# 检查CPU负载
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
check_result 0 "系统负载: $LOAD_AVG"

echo ""
echo "🎯 检查结果汇总"
echo "================================"
echo -e "✅ ${GREEN}通过: $PASS_COUNT${NC}"
echo -e "⚠️  ${YELLOW}警告: $WARN_COUNT${NC}"
echo -e "❌ ${RED}失败: $FAIL_COUNT${NC}"
echo ""

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "🎉 ${GREEN}恭喜！彩虹数据项目部署检查全部通过！${NC}"
    echo ""
    echo "🌐 访问信息："
    echo "- 网站首页: http://$(hostname -I | awk '{print $1}')/"
    echo "- API文档: http://$(hostname -I | awk '{print $1}')/api/docs/"
    echo "- Django管理: http://$(hostname -I | awk '{print $1}')/admin/"
    exit 0
elif [ "$FAIL_COUNT" -le 3 ]; then
    echo -e "⚠️  ${YELLOW}部署基本成功，但有少量问题需要修复${NC}"
    echo ""
    echo "🔧 建议操作："
    echo "1. 查看上述失败项目并逐一修复"
    echo "2. 检查相关服务日志"
    echo "3. 重新运行此检查脚本验证"
    exit 1
else
    echo -e "❌ ${RED}部署存在较多问题，需要重新配置${NC}"
    echo ""
    echo "🆘 建议操作："
    echo "1. 重新运行部署脚本"
    echo "2. 检查系统环境配置"
    echo "3. 查看详细错误日志"
    exit 2
fi 