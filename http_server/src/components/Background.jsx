import React from 'react';

const Background = ({ image }) => {
  // 兼容base64和普通url
  let bgStyle = {};
  if (image) {
    if (image.startsWith('data:image/')) {
      bgStyle.backgroundImage = `url(${image})`;
    } else {
      bgStyle.backgroundImage = `url('${image}')`;
    }
  }
  return (
    <div className="background-layer" style={bgStyle} />
  );
};

export default Background;
