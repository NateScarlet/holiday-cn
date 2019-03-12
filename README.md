# holiday-cn

[![Build Status](https://travis-ci.org/NateScarlet/holiday-cn.svg?branch=master)](https://travis-ci.org/NateScarlet/holiday-cn) [![Release](https://img.shields.io/github/release/NateScarlet/holiday-cn.svg)](https://github.com/NateScarlet/holiday-cn/releases/latest) [![CalVer](https://img.shields.io/badge/calver-YYYY.0M.0D-22bfda.svg)](http://calver.org) [![Maintainability](https://api.codeclimate.com/v1/badges/c8e9d9c51bd2d858c577/maintainability)](https://codeclimate.com/github/NateScarlet/holiday-cn/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/c8e9d9c51bd2d858c577/test_coverage)](https://codeclimate.com/github/NateScarlet/holiday-cn/test_coverage) ![Maintenance](https://img.shields.io/maintenance/yes/2019.svg)

中国法定节假日数据 自动每日抓取国务院公告

- [x] 提供 JSON 格式节假日数据
- [x] CI 自动更新
- [x] 数据变化时时自动发布新版本 ( `Watch` - `Release only` 以获取邮件提醒! )
- [x] [发布页面]提供 JSON 打包下载


数据格式:

```JSON格式说明
{
    year: Int, 年份
    papers: [String], 所用国务院文件网址列表
    days: [
        {
            name: String, 节日名称
            date: String, ISO 8601 日期
            isOffDay: Boolean, 是否为休息日
        }
    ]
}
```

## 通过互联网使用

数据地址格式:  
  
    https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{年份}.json  

## 作为 git 子模块使用

参见 [Git 工具 - 子模块](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)

[发布页面]: https://github.com/NateScarlet/holiday-cn/releases
