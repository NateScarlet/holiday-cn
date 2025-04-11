# holiday-cn

[![Build Status](https://github.com/NateScarlet/holiday-cn/workflows/CI/badge.svg)](https://github.com/NateScarlet/holiday-cn/actions)
[![Release](https://img.shields.io/github/release/NateScarlet/holiday-cn.svg)](https://github.com/NateScarlet/holiday-cn/releases/latest)
[![CalVer](https://img.shields.io/badge/calver-YYYY.0M.0D-22bfda.svg)](http://calver.org)
[![JSDelivr](https://data.jsdelivr.com/v1/package/gh/NateScarlet/holiday-cn/badge?style=rounded)](https://www.jsdelivr.com/package/gh/NateScarlet/holiday-cn)
![Maintenance](https://img.shields.io/maintenance/yes/2025.svg)

中国法定节假日数据 自动每日抓取国务院公告

- [x] 提供 JSON 格式节假日数据
- [x] CI 自动更新
- [x] 数据变化时自动发布新版本 ( `Watch` - `Release only` 以获取邮件提醒! )
- [x] [发布页面]提供 JSON 打包下载

数据格式:

[JSON Schema](./schema.json)

```TypeScript
interface Holidays {
  /** 完整年份, 整数。*/
  year: number;
  /** 所用国务院文件网址列表 */
  papers: string[];
  days: {
    /** 节日名称 */
    name: string;
    /** 日期, ISO 8601 格式 */
    date: string;
    /** 是否为休息日 */
    isOffDay: boolean;
  }[]
}
```

## 注意事项

- 年份是按照国务院文件标题年份而不是日期年份，12 月份的日期可能会被下一年的文件影响，因此应检查两个文件。

- `与周末连休` 的周末不是法定节假日，数据里不会包含，见[《全国年节及纪念日放假办法》](https://www.gov.cn/zhengce/content/202411/content_6986380.htm) [#213](https://github.com/NateScarlet/holiday-cn/issues/213#issuecomment-1869546011) [#221](https://github.com/NateScarlet/holiday-cn/issues/221)

## 通过互联网使用

提示：任何第三方服务都可能故障或停止服务，如果稳定性要求高请自己搭建静态文件服务。

数据地址格式:

`https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{年份}.json`

或使用 JSDelivr：

`https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{年份}.json`

`https://fastly.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{年份}.json`

也可尝试使用 [ghproxy](https://github.com/hunshcn/gh-proxy) 或其他 Github 加速：

`https://{ghproxy服务}/https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{年份}.json`

~~访问 github 不方便时可使用国内镜像仓库~~ 2022-08-05: coding 现在要求登录才能下载开源仓库的文件。

~~`https://natescarlet.coding.net/p/github/d/holiday-cn/git/raw/master/{年份}.json`~~

## ICalendar 订阅

网址格式参见上一节

`{年份}.ics` 为对应年份的节假日

`holiday-cn.ics` 为 3 年前至次年的节假日

感谢 @retanoj 的 ics 格式转换实现

## docker 部署

```shell
docker-compose up --build -d
```
#### ⚠️说明：运行完命令即结束运行

## 作为 git 子模块使用

参见 [Git 工具 - 子模块](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)

[发布页面]: https://github.com/NateScarlet/holiday-cn/releases
