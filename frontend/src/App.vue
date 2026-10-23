<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <n-layout position="absolute" style="height: 100vh">
          <n-layout-header bordered style="height: 56px; padding: 0 20px; display: flex; align-items: center; gap: 16px">
            <div style="font-weight: 700; font-size: 18px; letter-spacing: 1px">
              <span style="color: #e64646">wanc</span> 剧本工坊
            </div>
            <div style="color: #888; font-size: 13px">红果短剧 · 人设锁定 · 爆款节奏 · 投稿导出</div>
            <div style="flex: 1"></div>
            <router-link to="/" style="text-decoration: none; color: #666; font-size: 14px">项目列表</router-link>
          </n-layout-header>
          <n-layout-content :native-scrollbar="false" style="padding: 20px">
            <router-view />
          </n-layout-content>
        </n-layout>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { NConfigProvider, NMessageProvider, NDialogProvider, NLayout, NLayoutHeader, NLayoutContent } from 'naive-ui'

const themeOverrides = {
  common: {
    primaryColor: '#e64646',
    primaryColorHover: '#ef6a5b',
    primaryColorPressed: '#c9332e',
    primaryColorSuppl: '#e64646'
  }
}
</script>

<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; background: #f5f6f8; }
a { color: inherit; }
</style>
