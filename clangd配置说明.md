# Keil工程在Trae IDE中使用clangd配置说明

## ✨ 支持的芯片系列

- ✅ **STM32F1** 系列 (Cortex-M3)
- ✅ **STM32F4** 系列 (Cortex-M4)

脚本会自动识别芯片系列并选择正确的配置！

---

## 🚀 快速开始（推荐）

### 使用自动配置脚本

1. **复制脚本到新工程根目录**
   - 将 `setup_clangd.py` 复制到任何Keil STM32工程的根目录

2. **运行脚本**
   ```bash
   python setup_clangd.py
   ```

3. **重启clangd**
   - 按 `Ctrl+Shift+P`
   - 输入 "clangd"
   - 选择 **"clangd: Restart language server"**

---

## 📋 脚本功能（优化版）

`setup_clangd.py` 会自动：

- ✅ **从 Project.uvprojx 读取 IncludePath 和 Define**（精确匹配Keil配置）
- ✅ **从 <Cpu> 标签提取 CPU 类型**（M3/M4自动识别）
- ✅ **自动识别STM32系列（F1/F4）和型号**
- ✅ **添加 -mfloat-abi 和 -ffreestanding**（裸机工程优化）
- ✅ **检查并同步 USE_FULL_ASSERT**（宏一致性）
- ✅ **添加 -I. 提升鲁棒性**（支持根目录头文件）
- ✅ **去重并保持 Keil 一致的顺序**（减少符号冲突）
- ✅ 查找所有源代码目录和C源文件
- ✅ 生成 `.clangd` 配置文件
- ✅ 生成 `compile_commands.json` 编译命令数据库

---

## 🔄 日常使用注意

### 添加新文件/文件夹后

每当你添加了新的 **C源文件** 或 **源代码目录** 后：

1. **重新运行配置脚本**：
   ```bash
   python setup_clangd.py
   ```

2. **重启clangd**：
   - 按 `Ctrl+Shift+P`
   - 输入 "clangd"
   - 选择 **"clangd: Restart language server"**

---

## 📋 文件说明

- `setup_clangd.py` - ⭐⭐⭐ 自动配置脚本（核心文件，复制到其他工程使用）
- `.clangd` - clangd配置文件
- `compile_commands.json` - 编译命令数据库
- `clangd配置说明.md` - 本文档

---

## 🔧 手动配置（如果脚本无法使用）

### 文件1: `.clangd` 模板

```yaml
CompileFlags:
  Add:
    - "-target"
    - "arm-none-eabi"
    - "-mcpu=cortex-m3"
    - "-mthumb"
    - "-mfloat-abi=soft"
    - "-ffreestanding"
    - "-std=c99"
    - "-DSTM32F10X_MD"
    - "-DUSE_STDPERIPH_DRIVER"
    - "-DUSE_FULL_ASSERT"
    - "-I你的项目绝对路径"
    - "-I你的项目绝对路径/Start"
    - "-I你的项目绝对路径/Library"
    - "-I你的项目绝对路径/User"
    - "-I你的项目绝对路径/System"
    - "-I你的项目绝对路径/Hardware"
  Remove:
    - "-std=c++17"
Diagnostics:
  UnusedIncludes: None
  Suppress:
    - "implicit-function-declaration"
    - "unused-parameter"
    - "undeclared_var_use"
    - "unknown_typename"
    - "unused-include"
```

### STM32型号选择

根据你的芯片选择：
- `STM32F10X_LD` - 小容量 (16-32KB Flash)
- `STM32F10X_MD` - 中等容量 (64-128KB Flash) ⭐ 常用
- `STM32F10X_HD` - 大容量 (256-512KB Flash)
- `STM32F10X_XL` - 超大容量 (512-1024KB Flash)
- `STM32F10X_CL` - 互联型
- `STM32F40_41xxx` - STM32F40x/F41x
- `STM32F427_437xx` - STM32F427/F437
- `STM32F429_439xx` - STM32F429/F439
- `STM32F446xx` - STM32F446
- `STM32F469_479xx` - STM32F469/F479

---

## 💡 提示词（下次直接复制）

> "帮我在这个Keil STM32工程目录下运行 setup_clangd.py 配置clangd"
