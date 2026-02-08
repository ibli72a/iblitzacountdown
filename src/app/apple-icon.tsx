import { ImageResponse } from 'next/og';

// Route segment config
export const dynamic = 'force-static';

// Image metadata
export const size = {
  width: 180,
  height: 180,
};
export const contentType = 'image/png';

// Image generation
export default function Icon() {
  return new ImageResponse(
    (
      // ImageResponse JSX element
      <div
        style={{
          fontSize: 140,
          background: 'linear-gradient(135deg, #ff8a00 0%, #ee489a 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 700,
          fontFamily: 'system-ui',
        }}
      >
        I
      </div>
    ),
    // ImageResponse options
    {
      // For Apple icon support
      width: 180,
      height: 180,
    }
  );
} 