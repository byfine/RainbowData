#!/bin/bash
# 彩虹数据 (RainbowData) 前端构建脚本
# 用途：在本地构建Vue.js前端应用，准备部署文件
# 版本：v1.0
# 创建时间：2025年6月

set -e  # 遇到错误立即退出

echo "🖥️  开始构建彩虹数据前端应用..."

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/rainbow_data_frontend/rainbow-frontend"
BUILD_OUTPUT_DIR="$PROJECT_ROOT/deploy/frontend_dist"

echo "📍 项目目录信息："
echo "- 项目根目录: $PROJECT_ROOT"
echo "- 前端源码目录: $FRONTEND_DIR"
echo "- 构建输出目录: $BUILD_OUTPUT_DIR"

# 检查前端项目目录是否存在
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 前端项目目录不存在: $FRONTEND_DIR"
    echo "请确保Vue.js项目位于正确的目录下"
    exit 1
fi

# 进入前端项目目录
cd "$FRONTEND_DIR"

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "❌ 未找到package.json文件"
    echo "请确保这是一个有效的Vue.js项目"
    exit 1
fi

# 检查Node.js和npm
echo "🔧 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装，请先安装npm"
    exit 1
fi

echo "✅ Node.js版本: $(node --version)"
echo "✅ npm版本: $(npm --version)"

# 安装依赖
echo "📦 安装前端依赖包..."
npm install

# 检查是否有构建脚本
if ! npm run --silent | grep -q "build"; then
    echo "❌ 未找到build脚本，请检查package.json"
    exit 1
fi

# 设置生产环境变量
echo "⚙️  配置生产环境变量..."
export NODE_ENV=production

# 可选：创建.env.production文件用于生产环境配置
if [ ! -f ".env.production" ]; then
    cat > .env.production << 'EOF'
# 生产环境配置
NODE_ENV=production
VITE_API_BASE_URL=https://your-domain.com/api
VITE_APP_TITLE=彩虹数据 - 双色球数据分析平台
EOF
    echo "✅ 已创建.env.production配置文件"
    echo "⚠️  请根据实际域名修改VITE_API_BASE_URL"
fi

# 构建前端项目
echo "🔨 开始构建前端项目..."
npm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
    echo "❌ 构建失败，未找到dist目录"
    exit 1
fi

# 创建部署输出目录
mkdir -p "$BUILD_OUTPUT_DIR"

# 复制构建文件到部署目录
echo "📦 复制构建文件到部署目录..."
cp -r dist/* "$BUILD_OUTPUT_DIR/"

# 创建部署信息文件
cat > "$BUILD_OUTPUT_DIR/build_info.txt" << EOF
彩虹数据前端构建信息
==================
构建时间: $(date)
构建环境: $(uname -a)
Node.js版本: $(node --version)
npm版本: $(npm --version)
项目版本: $(npm pkg get version 2>/dev/null || echo "未知")
构建目录: $FRONTEND_DIR
输出目录: $BUILD_OUTPUT_DIR
EOF

# 显示构建文件大小
echo "📊 构建文件统计："
du -sh "$BUILD_OUTPUT_DIR"
echo ""
echo "📁 构建文件列表："
ls -la "$BUILD_OUTPUT_DIR"

# 验证重要文件是否存在
echo ""
echo "🔍 验证构建文件..."
REQUIRED_FILES=("index.html")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$BUILD_OUTPUT_DIR/$file" ]; then
        echo "✅ $file - 存在"
    else
        echo "❌ $file - 缺失"
    fi
done

# 检查静态资源目录
if [ -d "$BUILD_OUTPUT_DIR/assets" ]; then
    echo "✅ assets目录 - 存在 ($(ls -1 "$BUILD_OUTPUT_DIR/assets" | wc -l) 个文件)"
else
    echo "⚠️  assets目录 - 不存在或为空"
fi

echo ""
echo "🎉 前端构建完成！"
echo ""
echo "📋 部署准备："
echo "1. 构建文件位置: $BUILD_OUTPUT_DIR"
echo "2. 可以将该目录的内容上传到服务器的 /var/www/rainbow-data/frontend/ 目录"
echo ""
echo "📝 上传命令示例："
echo "scp -r $BUILD_OUTPUT_DIR/* your-username@your-server-ip:/tmp/"
echo "然后在服务器上执行："
echo "sudo cp -r /tmp/* /var/www/rainbow-data/frontend/"
echo "sudo chown -R rainbowdata:rainbowdata /var/www/rainbow-data/frontend/"
echo ""
echo "🔗 API配置提醒："
echo "请确保.env.production文件中的VITE_API_BASE_URL指向正确的后端API地址"
echo ""
echo "🚀 下一步："
echo "1. 上传构建文件到服务器"
echo "2. 配置Nginx指向前端文件目录"
echo "3. 重启Nginx服务" 