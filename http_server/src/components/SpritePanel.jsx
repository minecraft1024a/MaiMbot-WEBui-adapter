import React from 'react';

const SpritePanel = ({ sprite }) => {
  return (
    <div className="sprite-panel">
      {sprite ? <img src={sprite} alt="立绘" className="sprite-img" /> : <div className="sprite-placeholder">暂无立绘</div>}
    </div>
  );
};

export default SpritePanel;
