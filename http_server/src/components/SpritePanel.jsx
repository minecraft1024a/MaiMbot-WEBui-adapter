import React from 'react';

const SpritePanel = ({ sprite, onChange }) => {
  return (
    <div className="sprite-panel">
      {sprite ? <img src={sprite} alt="立绘" className="sprite-img" /> : <div className="sprite-placeholder">暂无立绘</div>}
      <div className="sprite-actions">
        <button onClick={() => onChange && onChange(prompt('输入立绘图片URL:'))}>切换立绘</button>
      </div>
    </div>
  );
};

export default SpritePanel;
