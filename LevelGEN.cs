using UnityEngine;
using System.Collections.Generic;

/*
 * Класс LevelGEN - совокупность методов для генерации масок-слоёв уровня (твёрдая поверхность, биом),
 * а также деформация исходного изображения, работа с оттенками, вычисление среднего значения цвета по изображению
 */
public class LevelGEN
{
    Texture2D map;
    private List<int> subLayer;

    public void SetMap(Texture2D m)
    {
        map = m;
    }

    public float[] getRGB(int x, int y)
    {
        Color color = map.GetPixel(x, y);
        float[] colors = new float[3] { color.r, color.g, color.b };
        return colors;
    }

    public float rgb2H(float r, float g, float b)
    {
        r /= 255;
        g /= 255;
        b /= 255;
        float cmax = Mathf.Max(r, g, b);
        float cmin = Mathf.Min(r, g, b);
        float diff = cmax - cmin;

        float h = 0;
        if (cmax == cmin)
            h = 0;
        else if (cmax == r)
            h = (60 * ((g - b) / diff) + 360) % 360;
        else if (cmax == g)
            h = (60 * ((b - r) / diff) + 120) % 360;
        else if (cmax == b)
            h = (60 * ((r - g) / diff) + 240) % 360;
        return h;
    }

    public float rgb2S(float r, float g, float b)
    {
        r /= 255;
        g /= 255;
        b /= 255;
        float cmax = Mathf.Max(r, g, b);
        float cmin = Mathf.Min(r, g, b);
        float diff = cmax - cmin;
        float s = 0;
        if (cmax != 0)
            s = (diff / cmax) * 100;
        return s;
    }

    public float rgb2V(float r, float g, float b)
    {
        r /= 255;
        g /= 255;
        b /= 255;
        float cmax = Mathf.Max(r, g, b);
        float v = cmax * 100;
        return v;
    }

    public float[] hsv2RGB(float h, float s, float v)
    {
        float hi = Mathf.Floor(h / 60) % 6;
        float vm = (100 - s) * v / 100;
        float a = (v - vm) * (h % 60) / 60;
        float vi = vm + a;
        float vd = v - a;
        float[] colors = new float[3];
        if (hi == 0)
        {
            colors[0] = v;
            colors[1] = vi;
            colors[2] = vm;
        }
        else if (hi == 1)
        {
            colors[0] = vd;
            colors[1] = v;
            colors[2] = vm;
        }
        else if (hi == 2)
        {
            colors[0] = vm;
            colors[1] = v;
            colors[2] = vi;
        }
        else if (hi == 3)
        {
            colors[0] = vm;
            colors[1] = vd;
            colors[2] = v;
        }
        else if (hi == 4)
        {
            colors[0] = vi;
            colors[1] = vm;
            colors[2] = v;
        }
        else
        {
            colors[0] = v;
            colors[1] = vm;
            colors[2] = vd;
        }
        colors[0] = colors[0] * 255 / 100;
        colors[1] = colors[1] * 255 / 100;
        colors[2] = colors[2] * 255 / 100;
        return colors;
    }

    public float[] middleColor(Texture2D image)
    {
        float mid = 0; float r = 0; float g = 0; float b = 0;
        float[] colors;
        Color c;
        for (int x = 0; x < image.width; x++)
        {
            for (int y = 0; y < image.height; y++)
            {
                c = image.GetPixel(x, y);
                r += c.r;
                g += c.g;
                b += c.b;
                mid = mid + ((r + g + b) / 3);
            }
        }
        r /= (image.width * image.height);
        g /= (image.width * image.height);
        b /= (image.width * image.height);
        mid = mid / (image.width * image.height);
        colors = new float[4] { r, g, b, mid };
        return colors;
    }


    public Color[][] biomLayer(Texture2D image)
    {
        Color[][] layer = new Color[image.width][];
        for (int x = 0; x < image.width; x++)
        {
            layer[x] = new Color[image.height];
            for (int y = 0; y < image.height; y++)
            {
                float[] colors = getRGB(x, y);
                float h = rgb2H(colors[0], colors[1], colors[2]);
                float[] new_colors = hsv2RGB(h, 100, 100);
                layer[x][y].r = new_colors[0];
                layer[x][y].g = new_colors[1];
                layer[x][y].b = new_colors[2];
                layer[x][y].a = 255;
            }
        }
        return layer;
    }

    public float[][] landscapeLayer(Texture2D image)
    {
        subLayer = new List<int>();
        float[][] layer = new float[image.width][];
        float[] colors_ = middleColor(image);
        float mid = rgb2V(colors_[0], colors_[1], colors_[2]);
        for (int x = 0; x < image.width; x++)
        {
            layer[x] = new float[image.height];
            for (int y = 0; y < image.height; y++)
            {
                float[] colors = getRGB(x, y);
                float v = rgb2V(colors[0], colors[1], colors[2]);
                if (v < mid)
                {
                    layer[x][y] = 1;
                    subLayer.Add(x*10000+y);
                }
                else layer[x][y] = 0;
            }
        }
        return layer;
    }

    public List<float> goalsGenerate(int count)
    {
        List<float> layer = new List <float>();
        for (int i = 0; i < count; i++)
        {
            int ind = Random.Range(0, subLayer.Count - 1);
            layer.Add(subLayer[ind]);
        }
        return layer;
    }

    public Texture2D ScaleTexture(Texture2D source, int targetWidth, int targetHeight)
    {
        Texture2D result = new Texture2D(targetWidth, targetHeight, source.format, false);
        float incX = (1.0f / (float)targetWidth);
        float incY = (1.0f / (float)targetHeight);
        for (int i = 0; i < result.height; ++i)
        {
            for (int j = 0; j < result.width; ++j)
            {
                Color newColor = source.GetPixelBilinear((float)j / (float)result.width, (float)i / (float)result.height);
                result.SetPixel(j, i, newColor);
            }
        }
        result.Apply();
        return result;
    }
}
