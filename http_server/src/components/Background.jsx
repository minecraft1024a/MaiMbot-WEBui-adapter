import React from 'react';

const Background = ({ image }) => {
  return (
    <div className="background-layer" style={{ backgroundImage: `url(${image})` }} />
  );
};

export default Background;
