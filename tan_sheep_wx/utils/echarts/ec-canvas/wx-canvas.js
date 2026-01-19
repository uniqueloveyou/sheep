/**
 * wx-canvas.js
 * ECharts 小程序 Canvas 适配器
 * 用于在小程序环境中适配 Canvas API
 */

class WxCanvas {
  constructor(ctx, canvasId, isNew, canvasNode) {
    this.ctx = ctx;
    this.canvasId = canvasId;
    this.chart = null;
    this.isNew = isNew;
    this.canvasNode = canvasNode;
    
    if (isNew) {
      // 新版本 Canvas 2D
      this.node = canvasNode;
    }
  }

  getContext(contextType) {
    if (contextType === '2d') {
      return this.ctx;
    }
    return this.ctx;
  }

  // 兼容旧版本 - 设置图表实例
  setChart(chart) {
    this.chart = chart;
  }

  // 兼容 DOM API
  addEventListener() {
    // 小程序不支持 addEventListener
  }

  removeEventListener() {
    // 小程序不支持 removeEventListener
  }

  getBoundingClientRect() {
    // 返回一个模拟的 bounding rect
    return {
      width: this.width || 0,
      height: this.height || 0,
      left: 0,
      top: 0,
      right: this.width || 0,
      bottom: this.height || 0
    };
  }

  attachEvent() {
    // 小程序不支持 attachEvent
  }

  detachEvent() {
    // 小程序不支持 detachEvent
  }
}

module.exports = WxCanvas;

